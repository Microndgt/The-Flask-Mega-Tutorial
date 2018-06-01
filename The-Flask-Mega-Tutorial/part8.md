The Flask Mega-Tutorial Part VIII: Followers
===

原文地址: [The Flask Mega-Tutorial Part VIII: Followers](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers)

这是 Flask Mega-Tutorial 系列的第 8 篇文章，在这里我将向你展示如何实现类似于 Twitter 以及其他社交网络的关注者功能。

在这章，我将继续使用应用的数据库。我希望应用的用户可以方便的选择它们想关注的其他用户。因此我将会扩展数据库来记录谁关注了谁，这个功能比你想象的要难。

本章的 Github 链接是：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.8), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.8.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.7...v0.8)


数据库关系回顾
===

我想来维护一个关注(followed)和关注者的用户列表。不幸的是，关系型数据库没有列表类型，有的只是拥有记录的表以及这些记录之间的关系。

`[译者注]`: 译者常用的 Postgresql 支持列表类型，JSON 类型等。

数据库有代表用户的表，因此现在需要做的是创建出一个能合适表达关注和关注者这种关系。那么现在最好是先回顾下最基本的数据库关系类型：

一对多
---

我已经在第四章使用了一对多类型，下面是这个关系的图表。

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch04-users-posts.png)

通过这种关系联结的两个实体是用户和文章。一个用户可能有多篇文章，但是一篇文章只有一个作者。这种关系在数据库中是通过在多那一头增加一个外键来表现的。在上面的关系中，外键是增加在 `posts` 表中的 `user_id` 字段。这个字段将每篇文章的记录和在用户表中的作者联系起来。

`user_id` 字段很清晰的提供了对某篇文章作者的直接访问，但是如果反方向呢？对于一个给定用户，展示他所有的文章，这种需求也是有用的。`posts` 表中的 `user_id` 字段同样足够来解决这个问题，为这个字段加上索引就可以通过高效的查询来得到某个用户的所有文章列表。

多对多
---

多对多关系就有点复杂了。比如，考虑一个数据库包含 `students` 和 `teachers`。我可以说一个学生有多个老师，也可以说一个老师有多个学生。就好像是从两个不同的角度来说的一对多关系。

对于这种关系类型，我首先能够对于给定一个学生查询到其老师列表，也可以查询到对于一个老师其学生列表。这种关系对于关系型数据库是比较复杂的，它不能通过给已有的表中添加外键实现。

这种多对多关系必须通过使用一个辅助表，被称为关联表来实现。下面是一个可以查询学生和老师的数据库例子：

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch08-students-teachers.png)

可能一开始它不是那么明显，关联表中有两个外键，这样就可以完成上面所述的查询了。

多对一和一对一
---

多对一关系类似于一对多关系。两者区别是这次是从多那一边看的。

一对一关系是一对多关系的特别情况。实现是类似的，但是在多那一边会有一个约束，保证了同一条记录只出现一次。虽然这种关系有一些比较有用的应用，但是没有其他类型的关系常用。

关注者
===

从上面的数据库关系类型介绍中可以看出，实现关注者合适的数据模型就是多对多关系，因为一个用户可能关注多个用户，而且一个用户也可能有多个关注者。但是又有些变化。在上面的多对多例子中，我有两个实体来实现多对多的关系。但是在关注者这个例子中，我只有用户这一个实体。那么多对多关系的第二个实体呢？

第二个实体当然也是用户了。一个类的实例和另一个同样类的实例之间的关系被称作自引用关系，也就是目前的情况。

下面就是自引用的多对多关系实现关注者的图表

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch08-followers-schema.png)

`followers` 表是多对多关系的关联表。表中的外键都指向了用户表的记录，表示用户和用户之间的联系。在这张表中的每一条记录都是一个关注者用户和被关注的用户。就像学生和老师的那个例子，这样的配置足够可以回答上面的问题了，而且非常简洁。

数据库模型表示
===

让我们首先将关联表 `followers` 添加到数据库中。下面是该表的定义：

```python
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)
```

这基本上是我上面数据库关系图表的直接翻译。注意到我没有将这个表声明为像 `users` 和 `posts` 那样的模型。因为这是一个辅助表，除了外键数据没有其他数据，因此我直接创建了这个表。

现在我可以在 `users` 表中声明多对多关系了:

```python
class User(UserMixin, db.Model):
    # ...
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
```

这个关系的配置也挺复杂。正如我之前在 `posts` 定义的一对多关系一样，这里我也在模型类中使用了 `db.relationship` 函数来定义关系。这个关系将一个 User 实例和另一个 User 实例联系在一起，也就是说这个关系关联了一对用户，左边的用户关注右边的用户。从用户对左边来看，该用户被定义为 `followed`(类变量)，因为从该关系的左侧查询你会得到该用户所有关注的人(也就是用户对右边的人)。让我们逐一的对 `db.relationship()` 的参数做出解释：

- `User` 是关系右侧实体(左侧实体是当前类)。因为这是一个自引用关系，因此在两边我使用了同样的类。
- `secondary` 配置了该关系的关联表，就是我上面定义的 `followers`。
- `primaryjoin` 表明了左侧实体(关注者)和关联表的联结条件。关系左侧的联结条件是用户 ID 和关联表中的 `follower_id` 字段一致。`followers.c.follower_id` 表达式引用了关联表的 `follower_id`列。
- `secondaryjoin` 表明了右侧实体(被关注者)和关联表的联结条件。该条件和 `primaryjoin` 类似，唯一不同是我现在使用了 `followed_id`，是关联表的另一个外键。
- `backref` 定义了如何从右侧实体获取该关系。从左侧来看，该关系被命名为 `followed`，那么从右侧我将使用 `followers` 来表示所有由右侧实体联结到的左侧用户列表。`lazy` 参数表明该查询的执行模式。`dynamic` 模式会等到特定的查询请求才会去查询，我在一对多关系中也配置了该模式。
- `lazy` 和 `backref` 中的参数是一样的，但是这里配置的是左侧查询。

如果这部分不好理解，不要担心。后面我会展示这些查询是怎么运行的，到时候一切云开雾散。

数据库的变化需要记录在一次新的数据库迁移中：

```shell
(venv) $ flask db migrate -m "followers"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'followers'
  Generating /home/miguel/microblog/migrations/versions/ae346256b650_followers.py ... done

(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 37f06a334dbf -> ae346256b650, followers
```

`[译者注]` 更多知识
---

- [flask-sqlalchemy 中的 lazy 的解释](http://shomy.top/2016/08/11/flask-sqlalchemy-relation-lazy/)
- [Basic Relationship Patterns](http://docs.sqlalchemy.org/en/rel_1_0/orm/basic_relationships.html)

添加和移除关注
===

幸亏有了 SQLAlchemy ORM，一个用户关注另一个用户可以以 `followed` 关系记录在数据库中，即使是一个关注用户列表。比如，我有两个用户 `user1` 和 `user2`，我可以用下面的方式来使得第一个用户关注第二个用户：

```python
user1.followed.append(user2)
```

停止关注该用户，可以：

```python
user1.followed.remove(user2)
```

即使添加和移除关注者是这样容易，我还是想继续提高代码复用率，不准备使用 `append` 和 `remove`。我将在 `User` 模型实现 `follow` 和 `unfollow` 方法。将应用逻辑从视图函数中移除并且放入模型或者其他辅助类和模块中，这样是好的做法，在后面你可以看到，这样会使得单元测试变得容易。

下面是用户模型的改变：

```python
class User(UserMixin, db.Model):
    #...

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
```

`follow()` 和 `unfollow()` 方法使用了关系对象中的 `append()` 和 `remove()` 方法，但是在调用之前会首先调用 `is_following` 方法来确保本次调用有效。比如我想让 `user1` 关注 `user2`，但是结果是该关注关系已经存在于数据库中，我不想重复添加关系。在 `unfollow` 也是同样的逻辑。

`is_following()` 方法对 `followed` 关系进行了一次查询检查两个用户之间的关系是否已经存在。`filter()` 方法比 `filter_by()`方法更低层次，`filter()` 可以包含筛选条件，不像 `filter_by()` 只能检查相等条件。我使用的条件是查询在关联表 的 `followed_id` 列中是否有和被关注者 `user` 相同的 ID。查询被 `count()` 终止，会返回查询结果的数目。该查询返回结果会是 0 或者 1，因此判断等于 1 或者大于 0，两者是等效的。其他我使用果的查询终止器是 `all()` 和 `first()`。 

获取关注用户的文章
===

数据库的用户关注支持基本完成了，但是其实错过了一个重要的功能。在应用首页我要展示所有关注用户的文章列表，因此我需要完成一个返回这些文章的数据库查询。

最明显的方法就是返回关注用户列表，`user.followed.all()`。然后对于每一个用户来查询他的文章。最后将每个用户的文章合并到单独的列表中，以时间排序。听起来不错？不，这样太低效。

这个方法有几个问题。如果这个用户关注了上千个其他用户？你需要进行上千次数据库查询吗？然后我需要合并上千个列表，然后排序？第二个问题，应用的首页需要进行分页，因此不能直接展示所有的文章。那么既然要按照时间排序，那么我该如何知道哪些文章是最近发表的，除非我获取所有文章然后排序？其实这是一个很烂的方法，一点都不可扩展。

虽然合并和排序是不可避免的，但是在应用中做会导致很低效的处理。这种工作正是关系型数据库所擅长的。数据库拥有可以使得查询和排序高效的索引。因此我需要做的是想出单条数据库查询定义我想要的信息，然后让数据库来配置提取信息最高效的方式。

下面你可以看到这条查询：

```python
class User(db.Model):
    #...
    def followed_posts(self):
        return Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Post.timestamp.desc())
```

这是到目前为止我使用最复杂的一个查询了。我将会逐个的解读这个查询。如果你仔细查看该查询的结构，你将会注意到这里有三个主要的部分：`join()`, `filter()` 和 `order_by()`

```python
Post.query.join(...).filter(...).order_by(...)
```

联结
---

为了理解一个联结操作做了什么，让我们先看一个例子。假定我有一个 User 表，包含以下内容：

id | username
---- | ---
1 | john
2 | susan
3 | mary
4 | david

为了简单起见，我没有显示用户模型的所有字段，只显示了查询必须的字段。

并且假定，`followers` 关联表假定了 join 关注了用户 susan 和 david，用户 susan 关注了 mary，用户 mary 关注了 david。数据表如下所示：

follower_id | followed_id
---- | ---
1 | 2
1 | 4
2 | 3
3 | 4

最后，文章表包含了每个用户的一篇文章

id | text | user_id
---- | --- | ---
1 | post from susan	| 2
1 | post from mary	| 3
2 | post from david	| 4
3 | post from john	| 1

该表也忽略了无关本次讨论的其他字段

下面是我之前查询中调用的 `join()`:

```python
Post.query.join(followers, (followers.c.followed_id == Post.user_id))
```

我在 `posts`(文章)表中进行了联结操作。第一个参数是 followers 关联表，第二个参数是联结条件。对于这个调用，数据库会创建一个将 posts 表数据和 followers 表数据组合起来的临时表。组合条件就是我传递进去的参数。

联结条件是 followers 表中的 `followed_id` 字段必须和 posts 表中的 `user_id` 字段一致。为了完成这个合并，数据库会从 posts 表中取出每一行数据(联结的左侧)，然后添加从 followers 表(联结的右侧)中匹配该条件的所有行。如果 followers 中有多行匹配该条件，post 也会出现多次。如果一个给定的 post 没有在 followers 中的匹配，那么该 post 记录就不会出现在 联结的结果集中。

对于上面的示例数据，联结操作的结果是：

id | text | user_id | follower_id | followed_id
---- | --- | --- | --- | ---
1 | post from susan	| 2 | 1 | 2
1 | post from mary	| 3 | 2 | 3
2 | post from david	| 4 | 1 | 4
3 | post from john	| 4 | 3 | 4

注意 `user_id` 和 `followed_id` 列的值是对应的，这就是联结条件。用户 john 没有出现在联结表中，是因为没有人关注 john。david 的文章出现了两次，因为有两个不同的用户关注了 david。

也许现在通过该联结做了什么还不是很清楚，但是请继续读下去，这仅仅是前面查询语句的一部分。

过滤
---

联结操作返回了某个用户关注的所有用户的文章列表，但是这些数据并不是我最终想要的。我仅仅对该列表的一部分感兴趣，即某一个用户关注的文章，因此我需要将不要的文章去除，那么就要用到 `filter()` 调用。

下面是查询的过滤部分：

```python
filter(followers.c.follower_id == self.id)
```

因为该查询是基于 User 类的，所以 `self.id` 表达式指代我感兴趣的用户的 ID。`filter()`调用在联结后的表中筛选 `follower_id` 和当前用户 ID 相同的记录，也就是我只保留了当前用户作为关注者的文章列表。

我们假定关注者是 `john`，他的 id 字段是 1。下面是筛选之后的联结表：

id | text | user_id | follower_id | followed_id
---- | --- | --- | --- | ---
1 | post from susan	| 2 | 1 | 2
2 | post from david	| 4 | 1 | 4

这正是我想要的文章列表！

记得该查询是基于 Post 类的，因此即使我在数据库创建的临时表处停止，结果也只会是临时表的 posts 部分，而不包含联结出来的额外列。

排序
---

查询的最后一步是对结果排序，排序部分如下：

```python
order_by(Post.timestamp.desc())
```

在这里我以文章创建时间降序排序。通过这样的排序，结果第一个就是最近创建的文章。

组合自己和关注用户的文章
===

在 `followed_posts()` 函数中的查询语句是很有用的，但是有一个限制。用户一般会希望在看到关注者文章的时间线的同时，也能看到自己的文章，但是目前该查询不能完成这一功能。

有两种方法来实现这个功能。最直接的方法是，让所有用户都关注自己，上面的查询就会将自己的文章也查询出来。这个方法的缺点在于会影响关注者的状态。所有的关注者数目会多一，因此需要在展示之前提前处理。第二种方法是单独查询用户自己的文章，然后使用 union 操作来将两个查询合并起来。

最后我选择了第二种方法。下面你可以看到 `followed_posts()` 函数已经通过 union 来扩展获取了用户自己的文章。

```python
def followed_posts(self):
    followed = Post.query.join(
        followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
    own = Post.query.filter_by(user_id=self.id)
    return followed.union(own).order_by(Post.timestamp.desc())
```

注意 `followed` 和 `own` 查询是如何在排序之前组合成一个的。

用户模型的单元测试
===

虽然我并不认为关注功能是一个很复杂的功能，但是也不简单。在我写一些比较复杂的代码的时候，我会考虑代码在将来当我在修改应用其他部分后能不能正常运行。最好的办法是创建一套自动化的测试，这样每次修改之后都能重新运行这些测试。

Python 提供了非常有用的 `unittest` 包来使得书写和执行单元测试变得容易。让我们在 `test.py` 模块中来创建对 `User` 类的单元测试吧。

```python
from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':
    unittest.main(verbosity=2)
```

现在我有四个测试包括：密码哈希，用户头像和关注功能。`setUp()` 和 `tearDown()` 方法是单元测试框架在测试之前和之后执行的特殊方法。我对 `setUp()` 方法有一些小的改动，阻止单元测试使用我开发中使用的数据库。通过将配置 `SQLALCHEMY_DATABASE_URI` 改为 `sqlite://`，SQLAlchemy 将在测试中使用 SQLite 内存数据库。`db.create_all()` 调用会创建数据库所有表。这是在脚本中创建数据库的快捷方式。在开发和生产环境中，我已经向你展示了如何通过数据库迁移来创建数据库表。

你可以通过下面的命令来执行整个测试：

```shell
(venv) $ python tests.py
test_avatar (__main__.UserModelCase) ... ok
test_follow (__main__.UserModelCase) ... ok
test_follow_posts (__main__.UserModelCase) ... ok
test_password_hashing (__main__.UserModelCase) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.494s

OK
```

从现在开始，任何时候改变应用之后，你都可以重新执行测试保证所有的测试都通过。而且，每当你添加一个功能，都应该添加对应的单元测试。

将关注功能整合到应用中
===

数据库和模型对关注功能的支持都基本完成，但是我还没有将这些功能整合到应用中。好消息是这件事很简单，都是基于你已经学习到的概念。

让我们先在应用中加入关注和取消关注一个用户的路由：

```python
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))
```

代码都很简单，主要关注一下错误检查，它会阻止可能的问题并且在问题发生的时候提供有用的信息。

视图函数已经就位，我就可以从应用的页面来链接到这两个路由。我将在每个用户的个人页面处添加关注和取消关注链接：

```html
...
<h1>User: {{ user.username }}</h1>
{% if user.about_me %}<p>{{ user.about_me }}</p>{% endif %}
{% if user.last_seen %}<p>Last seen on: {{ user.last_seen }}</p>{% endif %}
<p>{{ user.followers.count() }} followers, {{ user.followed.count() }} following.</p>
{% if user == current_user %}
<p><a href="{{ url_for('edit_profile') }}">Edit your profile</a></p>
{% elif not current_user.is_following(user) %}
<p><a href="{{ url_for('follow', username=user.username) }}">Follow</a></p>
{% else %}
<p><a href="{{ url_for('unfollow', username=user.username) }}">Unfollow</a></p>
{% endif %}
...
```

用户信息模版的改变是在上次登陆时间的下面增加了一行展示有多少关注者和该用户关注了多少人。并且在你查看自己的信息页面的时候的编辑按钮可能变成下面三种情况之一：

- 如果用户在看自己的信息页面，Edit 仍然和以前一样
- 如果用户查看没有关注的用户，这个按钮就是 Follow
- 如果用户查看已经关注的用户，这个按钮就是 Unfollow

现在你就可以运行应用，然后创建几个用户用来体验关注功能。唯一你需要记得的事情是你得自己去敲 URL 来跳转到不同用户，因为现在还没有一个用户列表页面。比如，如果你想查看 susan 用户，你需要键入 `http://localhost:5000/user/susan` 来查看 susan 的个人信息页面。记得查看在你关注或者取消关注后检查下关注者数量和关注的数量变化。

我应该可以在应用首页来展示关注用户的文章，但是现在功能还没有全部完成，因为用户还不能发表文章。所以等到以后功能完备之后才能进行。
