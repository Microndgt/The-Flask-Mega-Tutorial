The Flask Mega-Tutorial, Part IV Databases in Flask
===

原文地址: [The Flask Mega-Tutorial, Part IV Databases in Flask](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)

这是Flask Mega-Tutorial系列的第四部分，在这部分我将告诉你如何使用数据库。

Flask中的数据库
===

我相信你已经听说过，Flask本身不支持数据库。 这是Flask故意没有设计的组件之一，这很好，因为你可以自由选择最适合你的应用程序的数据库，而不是被迫去适应你的应用程序。

Python支持的数据库有很多，大部分都已经有了Flask对应的扩展，使数据库与应用程序可以很好的集成。 数据库可以分为两大组，遵循关系模型的（经典的比如MySQL），没有关系模型的。 后者通常被称为NoSQL，表明他们不支持SQL语句。 虽然两组都是很好的数据库产品，但我认为关系数据库对于具有结构化数据（如用户列表，博客帖子等）的应用程序来说是更好的选择，而NoSQL数据库往往更更适合结构不确定的数据。 这个Flask应用，像大多数应用一样，可以使用任何一种类型的数据库来实现，但是出于上面所述的原因，我打算使用关系数据库。

在第三章中，我向你展示了第一个Flask扩展。 在这一章中，我将使用另外两个扩展。第一个是 [Flask-SQLAlchemy](http://packages.python.org/Flask-SQLAlchemy) ，它是为 Flask 定制的 [SQLAlchemy](http://www.sqlalchemy.org/) ，它是一个[对象关系映射器](http://en.wikipedia.org/wiki/Object-relational_mapping) （ORM）。ORM 允许应用程序使用高级实体（如类，对象和方法）而不是表和 SQL 来管理数据库。 ORM 的工作是将高级操作转换成数据库命令。

SQLAlchemy 支持很多数据库引擎，包括流行的 MySQL ，PostgreSQL 和 SQLite 。这是非常强大的，因为你可以使用不需要服务器的 SQLite 数据库进行开发，然后在生产服务器上部署应用程序时，换成更强大的 MySQL 或 PostgreSQL 服务器，这一切都无需改变你的代码。

要在虚拟环境中安装Flask-SQLAlchemy，请确保先激活虚拟环境，然后运行：

`(venv) $ pip install flask-sqlalchemy `


数据库迁移
===
我所见过的大多数数据库教程都是关于如何创建和使用数据库的，但没有充分解决在应用程序需要更改或增长时更新现有数据库的问题。这很难，因为关系型数据库是以结构化数据为中心的，所以当结构发生变化时，已经在数据库中的数据需要被迁移到修改后的结构中。

我将在本章中介绍的第二个扩展是Flask-Migrate ，这个扩展是Alembic为SQLAlchemy写的的一个数据库迁移框架。这个扩展使你在数据库迁移的过程中只需要做很少的工作。

Flask-Migrate的安装过程与你所看到的其他扩展类似：

`(venv) $ pip install flask-migrate`

Flask-SQLAlchemy配置
===

在开发过程中，我将使用 SQLite 数据库。 SQLite 数据库是开发小型应用程序最方便的选择，有时可能不是那么小（几十M)，
因为每个数据库都存储在磁盘上的单个文件中，并且不需要像 MySQL 和 PostgreSQL 那样运行数据库服务器。

我们有两个新的配置项添加到配置文件中：

```
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

```

Flask-SQLAlchemy 扩展从`SQLALCHEMY_DATABASE_URI`配置变量中获取应用程序数据库的位置。从第3章可以看出，从环境变量中设置配置通常是一种很好的做法，并且当环境没有定义该变量的时候提供一个默认值。。在这种情况下，我从 `DATABASE_URL` 环境变量中获取数据库URL，如果没有定义，我将配置一个名为 app.db 的数据库，位于应用程序的主目录中，该目录存储在`basedir`变量中。

将`SQLALCHEMY_TRACK_MODIFICATIONS`配置选项设置为False可禁用我不需要的Flask-SQLAlchemy功能，即每次在数据库中进行更改时都会向应用程序发出信号。

数据库将由数据库实例在应用程序中声明(`db = SQLAlchemy(app)`)。数据库迁移引擎也将有一个实例（`migrate = Migrate(app, db)`）。

`app/__ init__.py`示例

```
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
```

 这些是在应用程序之后创建的，我已经对`app/__ init__.py`做了三处更改。 首先，我添加了一个代表数据库的数据库对象。 然后我添加了另一个代表迁移引擎的对象。大多数扩展名被初始化为这两个。 最后，我正在导入一个名为`models` 的新模块。 这个模块将定义数据库的结构。

数据库模型
===
将存储在数据库中的数据将由一组类（通常称为数据库模型）表示 。SQLAlchemy 中的ORM 层将完成从这些类创建的映射对象到对应数据库表中行的翻译。

我们先来创建一个代表用户的模型。 使用 [WWW SQL Designer](http://ondras.zarovi.cz/sql/demo/) 工具，我使用下图来表示我们想要在users表中使用的数据：


![用户表](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch04-users.png)

id字段通常在所有模型中，并被用作主键 。 数据库中的每个用户将被分配一个唯一的id值，存储在这个字段中。主键在大多数情况下是由数据库自动分配的，所以我只需要提供标记为主键的id字段。

`username`，`email`和`password_hash`字段定义为字符串（使用VARCHAR可变字符串 ，并指定其最大长度，以便数据库可以优化空间使用率）。虽然username和email字段可能被猜测出，但是password_hash字段值却可以十分复杂。 为了确定程序是十分安全的，密码不应该直接存在数据库里面，需要做加密操作（hash），说起来比较复杂，将是另一章的主题，所以现在不要关心。

现在根据上面的用户表，修改`app/models.py`文件
```
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)   
```
上面创建的User类继承自db.Model ，这是来自Flask-SQLAlchemy的所有模型的基类。这个类将几个字段定义为类变量，字段被创建为db.Column类的实例，它将字段类型作为参数，以及其他可选参数。例如，允许指示哪些字段是唯一索引，这非常重要，以便以后在数据库中快速搜索。

`__repr__`方法告诉Python如何打印这个类的对象，这对于调试是非常有用的。 你可以在下面的Python解释器会话中看到正在运行的`__repr__`方法：

```
>>> from app.models import User
>>> u = User(username='susan', email='susan@example.com')
>>> u
<User susan>
```

创建迁移存储库
===

在上一节中创建的模型类定义了此应用程序的初始数据库结构，但随着应用程序的不断发展，将会有一个需要改变的结构，很可能会增加新的字段，但有时也会修改或删除字段。Flask-Migrate 将以一种不需要从头重新创建数据库的方式进行更改。

为了完成这个看起来很困难的任务，Flask-Migrate 维护了一个迁移库 ，它是一个存储迁移脚本的目录。每次对数据库模式进行更改时，都会向存储库中添加一个迁移脚本，其中包含更改的详细信息。如果要将迁移应用到数据库，这些迁移脚本将按照创建的顺序执行。

Flask-Migrate通过flask运行迁移命令，你已经看过`flask run`，这是一个Flask的一个子命令。`flask db`子命令由`Flask-Migrate`添加，以管理与数据库迁移相关的所有事情。现在就让我们通过运行`flask db init`来创建迁移语句：

```
(venv) $ flask db init
  Creating directory /home/miguel/microblog/migrations ... done
  Creating directory /home/miguel/microblog/migrations/versions ... done
  Generating /home/miguel/microblog/migrations/alembic.ini ... done
  Generating /home/miguel/microblog/migrations/env.py ... done
  Generating /home/miguel/microblog/migrations/README ... done
  Generating /home/miguel/microblog/migrations/script.py.mako ... done
  Please edit configuration/connection/logging settings in
  '/home/miguel/microblog/migrations/alembic.ini' before proceeding.
```

请记住， flask 命令依赖于`FLASK_APP` 环境变量来知道Flask应用程序的位置。 对于这个应用程序，你想要设置`FLASK_APP=microblog.py`，如第1章所述 。

运行这个命令后，你会发现一个新的迁移目录，里面有几个文件和一个版本子目录。 所有这些文件应从现在开始作为你的项目的一部分，特别是应该添加到源代码管理。

第一个数据库迁移
===

迁移数据库语句后，就可以创建第一个数据库迁移，其中包括映射到User数据库模型的用户表。有两种方法来创建数据库迁移：手动或自动。要自动生成迁移，Flask-Migrate会将数据库模型定义的数据库结构与数据库中当前使用的结构进行比较。然后，生成迁移脚本，以使数据库模式与应用程序模型匹配。在这种情况下，如果没有以前的数据库，会把整个User模型添加到迁移脚本中。`flask db migrate`子命令生成这些自动迁移：
```
(venv) $ flask db migrate -m "users table"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_email' on '['email']'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_username' on '['username']'
  Generating /home/miguel/microblog/migrations/versions/e517276bb1c2_users_table.py ... done
```
命令的输出让你了解`Flask-Migrate`在迁移过程中做了什么工作。 前两行是信息性的，通常可以忽略。然后它说它找到了一个用户表和两个索引。然后它会告诉你在哪里写了迁移脚本。`e517276bb1c2`代码是一个自动生成的用于迁移的唯一代码（这对你来说会有所不同）。用-m选项给出的注释是可选的，它为迁移添加了一个简短的描述性文本。

生成的迁移脚本现在是项目的一部分，需要将其合并到源代码管理中。如果你好奇看看它的原理，可以看看文件的内容。你会发现它有两个函数叫做`upgrade()`和`downgrade()`。`upgrade()`函数应用迁移，而`downgrade()`函数将其回退。这样就可以在你后悔的时候回退到上一个版本

`flask db migrate`命令不会对数据库进行任何更改，只会生成迁移脚本。要将更改应用到数据库，必须使用`flask db upgrade`命令。

```
(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> e517276bb1c2, users table
```
由于此应用程序使用 SQLite， `upgrade`命令将检测到数据库不存在并将创建它（你会注意到在此命令完成后添加了一个名为`app.db`的文件，那就是 SQLite 数据库文件）。在使用数据库服务器（如 MySQL 和 PostgreSQL ）时，必须在运行`upgrade`之前在数据库服务器中创建数据库。

数据库升级和降级工作流程
===

虽然这个程序还处于开发阶段，但考虑到以后的数据表可能会更改，字段变更等，需要提前想好对策。假设在开发计算机上安装了应用程序，并且已将副本部署到生产服务器上。

比如有你的应用程序的下一版本必须对数据库模型进行更改，例如需要添加一个新表。如果没有自动迁移脚本，你需要弄清楚如何改变你的数据表，无论是在你的开发机器上，还是在你的服务器上，这可能是一个很大的工作。

但是通过数据库迁移支持，在程序中修改数据库模型之后，将生成一个新的迁移脚本（`flask db migrate`），有兴趣的话可以看看迁移脚本的内容，然后将更改后的数据库模型应用到开发数据库（`flask db upgrade`）。可以把迁移脚本添加到代码库并提交。

当准备将新版本的应用程序发布到生产服务器时，你只需要获取应用程序的更新版本（其中将包含新的迁移脚本），然后运行`flask db upgrade`。脚本将检测到生产数据库未更新到模式的最新版本，并运行在上一版本之后创建的所有新迁移脚本。

除了我前面提到的，还有有一个`flask db downgrade`命令，这个命令可以回退上次的迁移。虽然在生产系统上不太可能需要此选项，但在开发过程中它可能非常有用。当你已经生成了一个迁移脚本并将其应用，但是发现所做的更改并不完全符合需求。在这种情况下，可以降级数据库，删除迁移脚本，然后生成一个新的脚本替换它。

数据库关系
===

关系数据库擅长存储数据项之间的关系。考虑用户写博客文章的情况。用户将在users表中有记录，并且该帖子将在posts表中具有记录。记录谁写了哪一篇文章最有效的方法是链接两个相关表的记录。

一旦建立了用户和帖子之间的链接，数据库可以回答关于该链接的查询。比如说当你有博客文章，需要知道哪个用户写了什么，还有哪个用户都写了那些文章， Flask-SQLAlchemy 支持这两种类型的查询。

让我们展开数据库来存储博客文章，以查看实际中的关系。 以下是新posts表格的模式：
![post表](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch04-users-posts.png)


posts 表字段有所需的 id ，post 的内容和 timestamp。除此之外，我添加一个`user_id`字段，该字段链接到其作者。你已经看到所有的用户都有一个唯一的id主键。将博客文章链接到创作该博客文章的用户的方法是添加对用户id的引用，这正是`user_id`字段的作用。这个user_id字段被称为外键。上面的数据库图显示了外键作为它所引用表的字段和它的id字段之间的链接。 这种关系被称为一对多关系 ，因为“一个”用户写了“多”篇文章的关系。

修改后的app / models.py如下所示：
```
from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
```

新的 post 表将代表用户编写的博客文章。`timestamp`字段将被编入索引，如果你想按时间顺序检索帖子，这将非常有用。我还添加了一个`default`参数，并传给它`datetime.utcnow`函数。
当你将一个函数作为默认函数传递时，SQLAlchemy会将该字段设置为调用该函数的值，也就是当前的时间（请注意，在`utcnow`之后我没有包含()，所以我传递函数本身，而不是调用它的结果）。一般来说，你将需要在服务器应用程序中使用UTC日期和时间。这确保你使用统一的时间戳，而不管用户位于何处。 这些时间戳会在显示时转换为用户的当地时间。

`user_id`字段已初始化为`user.id`的外键，这意味着它引用了`users`表中的`id`值。 在这个引用中， `user`是数据库表的名称，`Flask-SQLAlchemy`自动将其设置为模型类的名称，并将其转换为小写字母。`User`类有一个新的`posts`字段，这是用`db.relationship`初始化的。这不是实际的数据库字段，而是用户和帖子之间关系的高级视图，因此它不在数据库图表中。 对于一对多关系， `db.relationship`字段通常在“one”一侧定义，并用作访问“many”的便捷方式。因此，例如，如果我有一个用户存储在u，表达式`u.posts`将运行一个数据库查询，返回该用户写的所有帖子。`db.relationship`的第一个参数表示代表关系“多”方面的类。`backref`参数定义了将被添加到指向 “one” 对象的 “many” 类的对象的字段的名称。这将添加一个`post.author`表达式，将返回给定的职位的用户。 `lazy`参数定义了关系的数据库查询将如何发布，这是我将在以后讨论的。不要担心，如果这些细节还没有多少意义，我会在本文末尾向你展示这方面的例子。

由于我已经更新了数据库模型，因此需要生成一个新的数据库迁移：

```
(venv) $ flask db migrate -m "posts table"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'post'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_post_timestamp' on '['timestamp']'
  Generating /home/miguel/microblog/migrations/versions/780739b227a7_posts_table.py ... done
```
而迁移需要应用于数据库：
```
(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade e517276bb1c2 -> 780739b227a7, posts table
```
如果你将项目存储在源代码管理中，请记住将新的迁移脚本添加到它。

交互shell
===
现在你已经定义数据库，但我没有告诉你如何添加和读取数据。由于应用程序还没有任何数据库逻辑，所以让我们先在Python解释器中使用命令行来熟悉它。接下来启动python解释器。在启动解释器之前，确保你的虚拟环境已被激活。

一旦进入 Python 提示符，让我们导入数据库实例和模型：
```
>>> from app import db
>>> from app.models import User, Post
```
首先创建一个新用户：
```
>>> u = User(username='john', email='john@example.com')
>>> db.session.add(u)·
>>> db.session.commit()
```
对数据库的更改是在会话的上下文中完成的，可以通过`db.session`访问。 会话中可以累积多个更改，当你确定要提交更改的时候，
可以发出一个运行`db.session.commit()` ，它以原子方式写入所有更改。

如果在任何时候处理会话时出现错误，调用`db.session.rollback()`将中止会话并删除存储在其中的所有更改。要记住的重要一点是，只有在`db.session.commit()`时才把更改写入数据库。 

让我们添加另一个用户：
```
>>> u = User(username='susan', email='susan@example.com')
>>> db.session.add(u)
>>> db.session.commit()
```

所有模型都有一个 query 属性，它是运行数据库查询的入口点。 最基本的查询是返回该类的所有元素`query.all()`

添加这些用户时， id 字段会自动设置为1和2。

```
>>> users = User.query.all()
>>> users
[<User john>, <User susan>]
>>> for u in users:
...     print(u.id, u.username)
...
1 john
2 susan
```
这是另一种查询方式。 如果你知道用户的 id ，则可以按照以下方式检索该用户：

```
>>> u = User.query.get(1)
>>> u
<User john>
```

现在我们来添加一个博客文章：

```
>>> u = User.query.get(1)
>>> p = Post(body='my first post!', author=u)
>>> db.session.add(p)
>>> db.session.commit()
```
我不需要为`timestamp`字段设置一个值，因为这个字段有一个默认值，你可以在模型定义中看到。那`user_id`字段呢？ 回想一下，我在`User`类中创建的`db.relationship`将`posts`属性添加到用户，并将`posts`属性添加到`posts`。我使用`author`虚拟字段将作者分配到`post`，而不必处理用户 ID 。SQLAlchemy 在这方面非常出色，因为它提供了对关系和外键的高级抽象。

接下来，我们来看看几个数据库查询：

```
>>> # get all posts written by a user
>>> u = User.query.get(1)
>>> u
<User john>
>>> posts = u.posts.all()
>>> posts
[<Post my first post!>]

>>> # same, but with a user that has no posts
>>> u = User.query.get(2)
>>> u
<User susan>
>>> u.posts.all()
[]

>>> # print post author and body for all posts 
>>> posts = Post.query.all()
>>> for p in posts:
...     print(p.id, p.author.username, p.body)
...
1 john my first post!

# get all users in reverse alphabetical order
>>> User.query.order_by(User.username.desc()).all()
[<User susan>, <User john>]
```
[Flask-SQLAlchemy](http://packages.python.org/Flask-SQLAlchemy/index.html)文档是了解可用于查询数据库的许多选项的最佳位置。

为了完成这个部分，让我们删除上面创建的测试用户和帖子，以便数据库干干净净并准备好下一章：

```
>>> users = User.query.all()
>>> for u in users:
...     db.session.delete(u)
...
>>> posts = Post.query.all()
>>> for p in posts:
...     db.session.delete(p)
...
>>> db.session.commit()
```

上下文
===
还记得在刚刚开始 Python 解释器之后你做了什么吗？ 你做的第一件事是导入一些模块入口：

```
>>> from app import db
>>> from app.models import User, Post
```
当你在写代码的时候，你需要经常在 Python shell 中测试，所以每次重复上面的导入都会变得枯燥乏味。`flask shell`命令是另一个非常有用的命令工具。 `shell`命令是`run`后由Flask执行的第二个“核心”命令。

这个命令的目的是在应用程序的上下文中启动一个 Python 解释器。看下面的例子：

```
(venv) $ python
>>> app
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'app' is not defined
>>>

(venv) $ flask shell
>>> app
<Flask 'app'>
```
使用常规的解释器会话，除非明确导入 app，否则不会知道 app 实例，但在使用 flask shell ，该命令会预先导入应用程序实例。`flask shell`不是它预先导入app ，而是你可以配置一个“外壳上下文”，这是一个预先导入其他符号的列表。

`microblog.py`中的以下函数将创建一个将数据库实例和模型添加到 shell 会话的上下文：

```
from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
```
`app.shell_context_processor decorator`将该函数注册为shell上下文函数。

当 flask shell 命令运行时，它将调用这个函数并在 shell 会话中注册它返回的项目。函数返回一个字典而不是一个列表，因为对于每个项目，你还必须提供一个名字，在shell中它将被引用，这是由字典的key给出的。

在添加 shell 上下文处理器函数后，你可以使用数据库实体，而无需导入它们：

```
(venv) $ flask shell
>>> db
<SQLAlchemy engine=sqlite:////Users/migu7781/Documents/dev/flask/microblog2/app.db>
>>> User
<class 'app.models.User'>
>>> Post
<class 'app.models.Post'>
```