The Flask Mega-Tutorial Part IV: Database
===

原文地址：[The Flask Mega-Tutorial Part IV: Database](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)

这是 Flask Mega-Tutorial 系列的第四部分，我将带你学习如何使用数据库(databases)。

**本章的内容极其重要！**大多数的应用都需要持久化存储数据，并高效地执行增删查改的操作，数据库便由此诞生了。

本章的 GitHub 链接为： [Browse](https://github.com/miguelgrinberg/microblog/tree/v0.4), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.4.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.3...v0.4).

Flsk 中的数据库
===

相信你已经听说过 Flask 天生不支持数据库。 和表单一样，这也是 Flask 有意而为之。对使用的数据库插件自由选择，让你拥有主动选择的权利，而不是被迫适应其中一种。

Python 中可选择的数据库有很多，它们中大部分都被封装成 Flask 插件以便更好地和 Flask 应用结合。数据库被划分为两大类，遵循关系模型的一类是关系数据库，另外的则是非关系数据库，简称***NoSQL***，表现在它们不支持流行的关系查询语言[SQL](https://en.wikipedia.org/wiki/SQL)。虽然两类数据库都是伟大的产品，但我认为关系数据库更适合具有结构化数据的应用程序，例如用户列表，用户动态等，而 NoSQL 数据库往往更适合非结构化数据。本文的应用像大多数人一样，可以使用任何一种类型的数据库来实现，但是出于上面所述的原因，我打算使用关系数据库。

在[第三章](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh/blob/master/docs/%E7%AC%AC%E4%B8%89%E7%AB%A0%EF%BC%9AWeb%E8%A1%A8%E5%8D%95.md)中，我向你展示了第一个 Flask 扩展，在本章中，我还要使用另外两个。 第一个是[Flask-SQLAlchemy](http://packages.python.org/Flask-SQLAlchemy)，这个插件为流行的[SQLAlchemy](http://www.sqlalchemy.org/)包做了一层封装以便在 Flask 中调用更方便，类似*SQLAlchemy*这样的包叫做[Object Relational Mapper](http://en.wikipedia.org/wiki/Object-relational_mapping)，简称ORM。 ORM允许应用程序使用高级实体（如类，对象和方法）而不是表和 SQL 来管理数据库。 ORM的工作就是将高级操作转换成数据库命令。

SQLAlchemy 不只是某一个数据库的ORM，而是支持包含[MySQL](https://www.mysql.com/)、[PostgreSQL](https://www.postgresql.org/)和[SQLite](https://www.sqlite.org/)在内的很多数据库软件。简直是太强大了，你可以在开发的时候使用简单易用且无需另起服务的 SQLite，需要部署应用到生产服务器上时，则选用更健壮的 MySQL 或 PotgreSQL 服务器，并且不需要修改应用代码。

在确认激活虚拟环境之后，利用如下命令来安装 Flask-SQLAlchemy 插件：
```shell
(venv) $ pip install flask-sqlalchemy
```

数据库迁移
===

我所见过的绝大多数数据库教程都是关于如何创建和使用数据库的，却没有指出当需要对现有数据库更新或者添加表结构时，应当如何应对。 这是一项困难的工作，因为关系数据库是以结构化数据为中心的，所以当结构发生变化时，数据库中的已有数据需要被迁移到修改后的结构中。

我将在本章中介绍的第二个插件是[Flask-Migrate](https://github.com/miguelgrinberg/flask-migrate)。 这个插件是[Alembic](https://bitbucket.org/zzzeek/alembic)的一个 Flask 封装，是 SQLAlchemy 的一个数据库迁移框架。 使用数据库迁移增加了启动数据库时候的一些工作，但这对将来的数据库结构稳健变更来说，是一个很小的代价。

安装 Flask-Migrte 和安装你见过的其他插件的方式一样：
```shell
(venv) $ pip install flask-migrate
```

Flask-SQLAlchemy 配置
===

开发阶段，我会使用 SQLite 数据库，SQLite 数据库是开发小型乃至中型应用最方便的选择，因为每个数据库都存储在磁盘上的单个文件中，并且不需要像 MySQL 和 PotgreSQL 那样运行数据库服务。

让我们给配置文件添加两个新的配置项：

```python
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Flask-SQLAlchemy 插件从`SQLALCHEMY_DATABASE_URI`配置变量中获取应用的数据库的位置。 当回顾[第三章](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh/blob/master/docs/%E7%AC%AC%E4%B8%89%E7%AB%A0%EF%BC%9AWeb%E8%A1%A8%E5%8D%95.md)可以发现，首先从环境变量获取配置变量，未获取到就使用默认值，这样做是一个好习惯。 本处，我从`DATABASE_URL`环境变量中获取数据库URL，如果没有定义，我将其配置为 `basedir` 变量表示的应用顶级目录下的一个名为*app.db*的文件路径。

`SQLALCHEMY_TRACK_MODIFICATIONS`配置项用于设置数据发生变更之后是否发送信号给应用，我不需要这项功能，因此将其设置为`False`。

数据库在应用的表现形式是一个*数据库实例*，数据库迁移引擎同样如此。它们将会在应用实例化之后进行实例化和注册操作。`app/__init__.py`文件变更如下：
```python
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

在这个初始化脚本中我更改了三处。首先，我添加了一个 `db` 对象来表示数据库。然后，我又添加了数据库迁移引擎`migrate`。这种注册 Flask 插件的模式希望你了然于胸，因为大多数 Flask 插件都是这样初始化的。最后，我在底部导入了一个名为 `models` 的模块，这个模块将会用来定义数据库结构。

数据库模型
===

定义数据库中一张表及其字段的类，通常叫做数据模型。ORM(SQLAlchemy)会将类的实例关联到数据库表中的数据行，并翻译相关操作。

就让我们从用户模型开始吧，利用 [WWW SQL Designer](http://ondras.zarovi.cz/sql/demo)工具，我画了一张图来设计用户表的各个字段（译者注：实际表名为 user）：

![用户表](http://upload-images.jianshu.io/upload_images/4961528-3d7f26d60dd340ad.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

`id` 字段通常存在于所有模型并用作*主键*。每个用户都会被数据库分配一个 id 值，并存储到这个字段中。大多数情况下，主键都是数据库自动赋值的，我只需要提供 `id` 字段作为主键即可。

`username`，`email`和`password_hash`字段被定义为字符串（数据库术语中的`VARCHAR`），并指定其最大长度，以便数据库可以优化空间使用率。 `username`和 `email` 字段的用途不言而喻，`password_hash`字段值得提一下。 我想确保我正在构建的应用采用安全最佳实践，因此我不会将用户密码明文存储在数据库中。 明文存储密码的问题是，如果数据库被攻破，攻击者就会获得密码，这对用户隐私来说可能是毁灭性的。 如果使用*哈希密码*，这就大大提高了安全性。 这将是另一章的主题，所以现在不需分心。

用户表构思完毕之后，我将其用代码实现，并存储到新建的模块*app/models.py*中，代码如下：
```python
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)    
```

上面创建的 User 类继承自db.Model，它是 Flask-SQLAlchemy 中所有模型的基类。 这个类将表的字段定义为类属性，字段被创建为`db.Column`类的实例，它传入字段类型以及其他可选参数，例如，可选参数中允许指示哪些字段是唯一的并且是可索引的，这对高效的数据检索十分重要。

该类的`__repr__`方法用于在调试时打印用户实例。在下面的 Python 交互式会话中你可以看到`__repr__()`方法的运行情况：
```shell
>>> from app.models import User
>>> u = User(username='susan', email='susan@example.com')
>>> u
<User susan>
```

创建数据库迁移存储库
===

上一节中创建的模型类定义了此应用程序的初始数据库结构（*元数据*）。 但随着应用的不断增长，很可能会新增、修改或删除数据库结构。 Alembic（Flask-Migrte 使用的迁移框架）将以一种不需要重新创建数据库的方式进行数据库结构的变更。

这是一个看起来相当艰巨的任务，为了实现它，Alembic 维护一个*数据库迁移存储库*，它是一个存储迁移脚本的目录。 每当对数据库结构进行更改后，都需要向存储库中添加一个包含更改的详细信息的迁移脚本。 当应用这些迁移脚本到数据库时，它们将按照创建的顺序执行。

Flask-Migrte 通过 `flask` 命令暴露来它的子命令。 你已经看过`flask run`，这是一个 Flask 本身的子命令。 Flask-Migrte 添加了`flask db`子命令来管理与数据库迁移相关的所有事情。 那么让我们通过运行`flask db init`来创建 microblog 的迁移存储库：
```shell
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

请记住，`flask`命令依赖于`FLASK_APP`环境变量来知道 Flask 应用入口在哪里。 对于本应用，正如[第一章](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh/blob/master/docs/%E7%AC%AC%E4%B8%80%E7%AB%A0%EF%BC%9AHello%2C%20World!.md)，你需要设置`FLASK_APP = microblog.py`。

运行迁移初始化命令之后，你会发现一个名为*migrations*的新目录。该目录中包含一个名为*versions*的子目录以及若干文件。从现在起，这些文件就是你项目的一部分了，应该添加到代码版本管理中去。

第一次数据库迁移
===

包含映射到 `User` 数据库模型的用户表的迁移存储库生成后，是时候创建第一次数据库迁移了。 有两种方法来创建数据库迁移：手动或自动。 要自动生成迁移，Alembic 会将数据库模型定义的数据库模式与数据库中当前使用的实际数据库模式进行比较。 然后，使用必要的更改来填充迁移脚本，以使数据库模式与应用程序模型匹配。 当前情况是，由于之前没有数据库，自动迁移将把整个 User 模型添加到迁移脚本中。 `flask db migrate`子命令生成这些自动迁移：
```shell
(venv) $ flask db migrate -m "users table"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_email' on '['email']'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_username' on '['username']'
  Generating /home/miguel/microblog/migrations/versions/e517276bb1c2_users_table.py ... done
```

通过命令输出，你可以了解到 Alembic 在创建迁移的过程中执行了哪些逻辑。前两行是常规信息，通常可以忽略。 之后的输出表明检测到了一个用户表和两个索引。 然后它会告诉你迁移脚本的输出路径。 `e517276bb1c2`是自动生成的一个用于迁移的唯一标识（你运行的结果会有所不同）。 `-m`可选参数为迁移添加了一个简短的注释。

生成的迁移脚本现在是你项目的一部分了，需要将其合并到源代码管理中。 如果你好奇，并检查了它的代码，就会发现它有两个函数叫`upgrade()`和`downgrade()`。 `upgrade()`函数应用迁移，`downgrade()`函数回滚迁移。 Alembic 通过使用降级方法可以将数据库迁移到历史中的任何点，甚至迁移到较旧的版本。

`flask db migrate`命令不会对数据库进行任何更改，只会生成迁移脚本。 要将更改应用到数据库，必须使用`flask db upgrade`命令。
```shell
(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> e517276bb1c2, users table
```

因为本应用使用 SQLite，所以 `upgrade` 命令检测到数据库不存在时，会创建它（在这个命令完成之后，你会注意到一个名为*app.db*的文件，即 SQLite 数据库）。 在使用类似 MySQL 和 PotgreSQL 的数据库服务时，必须在运行 `upgrade` 之前在数据库服务器上创建数据库。

数据库升级和降级流程
===

目前，本应用还处于初期阶段，但讨论一下未来的数据库迁移战略也无伤大雅。 假设你的开发计算机上存有应用的源代码，并且还将其部署到生产服务器上，运行应用并上线提供服务。

而应用在下一个版本必须对模型进行更改，例如需要添加一个新表。 如果没有迁移机制，这将需要做许多工作。无论是在你的开发机器上，还是在你的服务器上，都需要弄清楚如何变更你的数据库结构才能完成这项任务。

通过数据库迁移机制的支持，在你修改应用中的模型之后，将生成一个新的迁移脚本（`flask db migrate`），你可能会审查它以确保自动生成的正确性，然后将更改应用到你的开发数据库（`flask db upgrade`）。 测试无误后，将迁移脚本添加到源代码管理并提交。

当准备将新版本的应用发布到生产服务器时，你只需要获取包含新增迁移脚本的更新版本的应用，然后运行`flask db upgrade`即可。 Alembic 将检测到生产数据库未更新到最新版本，并运行在上一版本之后创建的所有新增迁移脚本。

正如我前面提到的，`flask db downgrade`命令可以回滚上次的迁移。 虽然在生产系统上不太可能需要此选项，但在开发过程中可能会发现它非常有用。 你可能已经生成了一个迁移脚本并将其应用，只是发现所做的更改并不完全是你所需要的。 在这种情况下，可以降级数据库，删除迁移脚本，然后生成一个新的来替换它。

数据库关系
===

关系数据库擅长存储数据项之间的关系。 考虑用户发表动态的情况， 用户将在 `user` 表中有一个记录，并且这条用户动态将在 `post` 表中有一个记录。 标记谁写了一个给定的动态的最有效的方法是链接两个相关的记录。

一旦建立了用户和动态之间的关系，数据库就可以在查询中展示它。最小的例子就是当你看一条用户动态的时候需要知道是谁写的。一个更复杂的查询是， 如果你好奇一个用户时，你可能想知道这个用户写的所有动态。 Flask-SQLAlchemy 有助于实现这两种查询。

让我们扩展数据库来存储用户动态，以查看实际中的关系。 这是一个新表 `post` 的设计（译者注：实际表名分别为 user 和 post）：

![数据库关系](http://upload-images.jianshu.io/upload_images/4961528-7057ec250f40bed5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

`post` 表将具有必须的`id`、用户动态的 `body` 和 `timestamp` 字段。 除了这些预期的字段之外，我还添加了一个`user_id`字段，将该用户动态链接到其作者。 你已经看到所有用户都有一个唯一的 `id` 主键， 将用户动态链接到其作者的方法是添加对用户 `id` 的引用，这正是`user_id`字段所在的位置。 这个`user_id`字段被称为*外键*。 上面的数据库图显示了外键作为该字段和它引用的表的 `id` 字段之间的链接。 这种关系被称为*一对多*，因为“一个”用户写了“多”条动态。

修改后的*app/models.py*如下：
```python
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

新的“Post”类表示用户发表的动态。 `timestamp`字段将被编入索引，如果你想按时间顺序检索用户动态，这将非常有用。 我还为其添加了一个 `default` 参数，并传入了`datetime.utcnow`函数。 当你将一个函数作为默认值传入后，SQLAlchemy 会将该字段设置为调用该函数的值（请注意，在 `utcnow` 之后我没有包含`()`，所以我传递函数本身，而不是调用它的结果）。 通常，在服务应用中使用 UTC 日期和时间是推荐做法。 这可以确保你使用统一的时间戳，无论用户位于何处，这些时间戳会在显示时转换为用户的当地时间。

`user_id`字段被初始化为`user.id`的外键，这意味着它引用了来自用户表的 `id` 值。本处的 `user` 是数据库表的名称，Flask-SQLAlchemy 自动设置类名为小写来作为对应表的名称。 `User`类有一个新的 `posts` 字段，用`db.relationship`初始化。这不是实际的数据库字段，而是用户和其动态之间关系的高级视图，因此它不在数据库图表中。对于一对多关系，`db.relationship`字段通常在“一”的这边定义，并用作访问“多”的便捷方式。因此，如果我有一个用户实例`u`，表达式`u.posts`将运行一个数据库查询，返回该用户发表过的所有动态。 `db.relationship`的第一个参数表示代表关系“多”的类。 `backref`参数定义了代表“多”的类的实例反向调用“一”的时候的属性名称。这将会为用户动态添加一个属性`post.author`，调用它将返回给该用户动态的用户实例。 `lazy`参数定义了这种关系调用的数据库查询是如何执行的，这个我会在后面讨论。不要觉得这些细节没什么意思，本章的结尾将会给出对应的例子。

一旦我变更了应用模型，就需要生成一个新的数据库迁移：
```shell
(venv) $ flask db migrate -m "posts table"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'post'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_post_timestamp' on '['timestamp']'
  Generating /home/miguel/microblog/migrations/versions/780739b227a7_posts_table.py ... done
```

并将这个迁移应用到数据库：
```shell
(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade e517276bb1c2 -> 780739b227a7, posts table
```

如果你对项目使用了版本控制，记得将新的迁移脚本添加进去并提交。

表演时刻
===

经历了一个漫长的过程来定义数据库，我却还没向你展示它们如何使用。 由于应用还没有任何数据库逻辑，所以让我们在 Python 解释器中来使用以便熟悉它。 立即运行 `python` 命令来启动 Python（在启动解释器之前，确保您的虚拟环境已被激活）。 

进入 Python 交互式环境后，导入数据库实例和模型：
```shell
>>> from app import db
>>> from app.models import User, Post
```

开始阶段，创建一个新用户：
```shell
>>> u = User(username='john', email='john@example.com')
>>> db.session.add(u)
>>> db.session.commit()
```

对数据库的更改是在会话的上下文中完成的，你可以通过`db.session`进行访问验证。 允许在会话中累积多个更改，一旦所有更改都被注册，你可以发出一个指令`db.session.commit()`来以原子方式写入所有更改。 如果在会话执行的任何时候出现错误，调用`db.session.rollback()`会中止会话并删除存储在其中的所有更改。 要记住的重要一点是，只有在调用`db.session.commit()`时才会将更改写入数据库。 会话可以保证数据库永远不会处于不一致的状态。

添加另一个用户：
```shell
>>> u = User(username='susan', email='susan@example.com')
>>> db.session.add(u)
>>> db.session.commit()
```

数据库执行返回所有用户的查询：
```shell
>>> users = User.query.all()
>>> users
[<User john>, <User susan>]
>>> for u in users:
...     print(u.id, u.username)
...
1 john
2 susan
```

所有模型都有一个 `query` 属性，它是运行数据库查询的入口。 最基本的查询就是返回该类的所有元素，它被适当地命名为`all()`。 请注意，添加这些用户时，它们的 `id` 字段依次自动设置为 1 和2。

另外一种查询方式是，如果你知道用户的`id`，可以用以下方式直接获取用户实例：
```shell
>>> u = User.query.get(1)
>>> u
<User john>
```

现在添加一条用户动态：
```shell
>>> u = User.query.get(1)
>>> p = Post(body='my first post!', author=u)
>>> db.session.add(p)
>>> db.session.commit()
```

我不需要为 `timestamp` 字段设置一个值，因为这个字段有一个默认值，你可以在模型定义中看到。 那么`user_id`字段呢？ 回想一下，我在 `User` 类中创建的`db.relationship`为用户添加了 `posts` 属性，并为用户动态添加了 `author` 属性。 我使用 `author` 虚拟字段来调用其作者，而不必通过用户 ID 来处理。 SQLAlchemy 在这方面非常出色，因为它提供了对关系和外键的高级抽象。

为了完成演示，让我们看看另外的数据库查询案例：
```shell
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

[Flask-SQLAlchemy](http://packages.python.org/Flask-SQLAlchemy/index.html)文档是学习其对应操作的最好去处。

学完本节内容，我们需要清除这些测试用户和用户动态，以便保持数据整洁和为下一章做好准备：
```shell
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

## Shell 上下文

还记得上一节的启动 Python 解释器之后你做过什么吗？第一件事是运行两条导入语句：
```shell
>>> from app import db
>>> from app.models import User, Post
```

开发应用时，你经常会在 Python shell 中测试，所以每次重复上面的导入都会变得枯燥乏味。 `flask shell`命令是 `flask` 命令集中的另一个非常有用的工具。 `shell`命令是 Flask 在继 `run` 之后的实现第二个“核心”命令。 这个命令的目的是在应用的上下文中启动一个 Python 解释器。 这意味着什么？ 看下面的例子：
```shell
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

使用常规的解释器会话时，除非明确地被导入，否则 `app` 对象是未知的，但是当使用`flask shell`时，该命令预先导入应用实例。 `flask shell`的绝妙之处不在于它预先导入了`app`，而是你可以配置一个“shell 上下文”，也就是可以预先导入一份对象列表。

在*microblog.py*中实现一个函数，它通过添加数据库实例和模型来创建了一个 shell 上下文环境：
```python
from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
```

`app.shell_context_processor`装饰器将该函数注册为一个 shell 上下文函数。 当`flask shell`命令运行时，它会调用这个函数并在 shell 会话中注册它返回的项目。 函数返回一个字典而不是一个列表，原因是对于每个项目，你必须通过字典的键提供一个名称以便在 shell 中被调用。

在添加 shell 上下文处理器函数后，你无需导入就可以使用数据库实例：
```shell
(venv) $ flask shell
>>> db
<SQLAlchemy engine=sqlite:////Users/migu7781/Documents/dev/flask/microblog2/app.db>
>>> User
<class 'app.models.User'>
>>> Post
<class 'app.models.Post'>
```

