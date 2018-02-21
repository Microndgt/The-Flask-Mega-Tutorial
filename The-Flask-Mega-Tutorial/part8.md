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
