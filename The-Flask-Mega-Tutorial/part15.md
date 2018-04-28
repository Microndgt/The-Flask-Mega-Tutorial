The Flask Mega-Tutorial Part XV: A Better Application Structure
===

原文地址: [The Flask Mega-Tutorial Part XV: A Better Application Structure](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure)

这是 Flask Mega-Tutorial 系列的第十五篇文章了，在这里我将使用一种适合更大型应用的风格来重构应用。

目前博客应用的大小适中，所以我考虑现在是讨论 Flask 应用如何增长但是不会导致太混乱以致无法管理的好时候。Flask 是一个提供给你以任意方式组织项目的框架，而且作为它的设计哲学，它也使得当应用变大的时候改变或者调整应用结构成为可能，或者当你的需求，经验层级改变的时候。

在本章我将讨论一些应用于大型应用的一些模式，为了说明它们我将对我的博客项目的结构做一些改变，让代码变得更加可维护并且组织良好。当然，以真正的 Flask 精神，我鼓励你在组织你自己的项目的时候将这些改变作为一个建议。

本章的 Github 链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.15), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.15.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.14...v0.15)

当前的限制
===

应用在当前状态下主要有两个基本问题。如果你查看应用是如何组织的，你将会注意到应用目前有几个不同的子系统，但是它们的代码都是混在一起的，没有明确的界限，让我们分析下这些子系统都是什么：

- 用户验证子系统，包含一些在 `app/routes.py` 下的一些视图函数，在 `app/forms.py` 下的一些表单，在 `app/templates` 下的一些模板以及在 `app/email.py` 下的电子邮件支持
- 错误处理子系统，在 `app/errors.py` 中定义的错误处理器以及 `app/templates` 下的模板
- 核心应用功能，包含展示，创建和更新博客文章，用户资料和用户关注关系，以及博客文章的即时翻译，这些功能遍布应用的大部分模块和模板中。

仔细考虑下这三个子系统以及它们是如何组织的，你应该会注意到一个模式。我目前遵循的组织逻辑是基于每个模块专注于不同的应用功能。比如有模块专门处理视图函数，另一个模块用于 web 表单，一个用于错误，另一个用于电子邮件，一个目录用于 HTML 模板等等。这样的结构对于小的项目是满足的，但是一旦项目开始增长，这将会导致这些模块非常大而且混乱。

一种能清晰的看到这个问题的方式是考虑通过重用这个项目的代码来重新开始另一个项目。比如，用户验证部分应该在其他应用是可以正常工作的，但是如果你想使用这部分带啊吗，你需要去好几个不同的模块里去复制粘贴对应部分的代码到新项目的文件里。很不方便吧？如果用户验证相关的文件和应用其他部分是分开的话岂不是更好？Flask 的 `blueprints` 特性帮助实现一个更加可用的组织方式并且使得重用代码变的容易。

第二个问题不是那么明显。Flask 应用实例是在 `app/__init__.py` 中以全局变量的形式创建的，然后被导入到了许多应用模块里。当然这并不是一个问题，但是以全局变量的形式创建应用会使得一些场景变得复杂，比如测试。想象下你想在不同的配置下测试你的应用。因为应用是以全局变量的形式定义的，所以你没法使用不同的环境变量来实例化两套应用。另外所有的测试都使用同样的应用是不合适的，一个测试可能会对应用作出改变，这样会影响后面测试的运行。理想情况是所有的测试都在全新的应用实例上运行。

你可以在 `tests.py` 中看到我在应用已经设置配置之后改变配置，从而使得应用使用内存数据库而不是默认的 SQLite 数据库。我确实没有其他办法来改变配置的数据库，因为在测试启动的时候应用已经创建并且配置好了。对于这种特定的情况，在配置已经应用到应用上之后改变配置是可以正常工作的。但是在其他情况下，无论如何，它都是一个糟糕的方法，因为可能导致晦涩并且难以发现的问题。

更好的方式是不要使用全局变量来创建应用，而是在运行的时候使用应用工厂函数来创建。这是一个接受配置对象为参数的函数，并且会返回一个已经配置的 Flask 应用实例。如果我修改应用以采用应用工厂函数，那么对于需要不同配置的测试用例将非常容易，因为每个测试都可以创建它自己的应用。

在这章，我将重构应用，使用蓝图和应用工厂函数。展示出修改的每一个细节是不切实际的，因此我将讨论重构的步骤，之后你可以下载应用来详细查看修改的细节。

蓝图
===

在 Flask 中，蓝图是一个逻辑结构来展示应用的一个子集。一个蓝图中可以包含路由，视图函数，表单，模板以及静态文件。如果你在一个单独的 Python 包中写一个蓝图，那么你将会拥有一个将应用特定功能相关元素压缩在一起的组件。

蓝图的内容一开始是处于未激活状态的。为了将这些元素联系起来，蓝图需要在应用中注册。在注册的过程中，所有添加到蓝图的元素将会传递到应用中。因此你可以将蓝图作为应用的临时存储功能用来帮助组织你的代码。

错误处理蓝图
---

我创建的第一个蓝图是包含错误处理器的蓝图。这个蓝图的结构如下：

```
app/
    errors/                             <-- blueprint package
        __init__.py                     <-- blueprint creation
        handlers.py                     <-- error handlers
    templates/
        errors/                         <-- error templates
            404.html
            500.html
    __init__.py                         <-- blueprint registration
```

本质上，我是将 `app/errors.py` 模块移到了 `app/errors/handlers.py` 中，然后将两个错误模板移到了 `app/templates/errors`，这样它们就和其他模板分开了。我还需要在错误处理器中修改 `render_template()` 调用，使用新的错误模板路径。在这之后我将蓝图的创建放在了 `app/errors/__init__.py` 模块中，然后在应用实例创建之后在 `app/__init__.py` 中注册蓝图。

我应该注明 Flask 的蓝图是可以被配置来拥有独立的模版和静态文件的文件夹的。我决定将模板移到应用的模版文件夹的子文件夹下是为了让所有的模版都处于单层级下，但是如果你更喜欢将模版放在属于它的蓝图里面，也是可以的。比如，如果你在 `Blueprint()` 构造器中传递 `template_folder='templates'` 参数就可以在 `app/errors/templates` 下存储该蓝图的模板文件了。

创建一个蓝图和创建一个应用是很相似的。这一工作是在蓝图包的 `__init__.py` 模块中完成的：

```python
from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers
```

`Blueprint` 类接收蓝图的名字以及基模块的名字(一般和 Flask 应用实例一样，传递 `__name__`)，还有一些可选的参数，在这里我不需要。在蓝图对象被创建之后，我将导入 `handlers.py` 模块，这样错误处理器就会注册到蓝图中。在底部导入是为了避免循环导入。

在 `handlers.py` 模块中，使用 `@bp.app_errorhandler` 装饰器而不是使用应用的 `@app.errorhandler` 装饰器。虽然最后的结果是一样的，但是这样做会使得应用的路由是蓝图独立的，这样会更容易扩展。我同样需要修改两个错误模板的路径。

最后一步是将蓝图注册到应用上：

```python
app = Flask(__name__)

# ...

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

# ...

from app import routes, models  # <-- remove errors from this import!
```

为了注册一个蓝图，使用了 Flask 应用的 `register_blueprint()` 方法。当一个蓝图被注册之后，任何视图函数，模板，静态文件，错误处理器都会连接到应用上。我在 `app.register_blueprint()` 上面导入蓝图是为了防止循环依赖。

认证蓝图
---

将应用的认证函数重构成蓝图基本上和错误处理器一样。下面是重构后蓝图的图示：

```
app/
    auth/                               <-- blueprint package
        __init__.py                     <-- blueprint creation
        email.py                        <-- authentication emails
        forms.py                        <-- authentication forms
        routes.py                       <-- authentication routes
    templates/
        auth/                           <-- blueprint templates
            login.html
            register.html
            reset_password_request.html
            reset_password.html
    __init__.py                         <-- blueprint registration
```

为了创建这个蓝图，我必须将所有认证相关的功能移到我在这个蓝图创建的新的模块中。这包含一些视图函数，web 表单和一些支持函数，比如通过 email 来发送密码重置 token 的函数。我也将模板移到了应用的模板下面的子目录里，就和错误页面一样。

当在蓝图中定义路由的时候，使用 `@bp.route` 装饰器而不是 `@app.route`。另外在使用 `url_for()` 构建 URL 的时候也有语法上的变化。对于一般的直接绑定到应用上的视图函数来说，`url_for()` 函数的第一个参数是视图函数的名字。当在一个蓝图中定义一个路由的时候，参数必须包含蓝图名和视图函数名，通过 `.` 来分隔。因此比如，我需要将 `url_for('login')` 都替换成 `url_for('auth.login')`，其他的视图函数也是一样。

为了在应用上注册 `auth` 蓝图，我使用了稍微不同的形式：

```python
from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
```

`register_blueprint` 函数调用出现了额外的参数，`url_prefix`，这是可选参数，给定这个参数之后，每一个通过该蓝图定义的路由都会在 URL 加上这个前缀。在很多情况下，这是一种命名空间，保证了在该蓝图下的路由和应用中的或者其他蓝图中的路由分离。对认证来说，我认为所有的路由都以 `/auth` 开始会更好，因此我添加了这个前缀。因此现在登陆 URL 变成了 `http://localhost:5000/auth/login`。因为我使用了 `url_for()` 来生成 URL，所以所有的 URL 都会自动的添加上这个前缀。

主应用蓝图
---

第三个蓝图包含了核心应用逻辑。重构这部分和上面两个蓝图的构建方法一样。我将这个蓝图命名为 main，因此所有的 `url_for()` 调用都需要在视图函数名前面加上 `main.` 前缀。因为这是应用的核心功能，所以我决定将模板放在原来的位置不变。因为我已经将其他两个蓝图的模板放在了相应的子文件夹下，所以这样做没问题。

应用工厂模式
===

正如我在本章开始时所说，将应用对象作为全局变量会导致一些问题，主要是在一些测试场景上有一定的限制。在我介绍蓝图之前，应用不得不是全局变量，因为所有的视图函数和错误处理器必须被 `app` 的装饰器装饰，比如 `@app.route`。但是现在所有的路由和错误处理器都被移到了蓝图中，那么此时就应该改变把应用对象作为全局变量这种方式。

我将要做的是，添加一个函数叫做 `create_app()` 来创建一个 Flask 应用对象，并且移除全局变量。转换稍微有点复杂，我会挑选一些复杂的部分，但是首先我们先来看看这个应用工厂函数。

```python
# ...
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # ... no changes to blueprint registration

    if not app.debug and not app.testing:
        # ... no changes to logging setup

    return app
```

你已经看到了大多数 Flask 扩展都是通过创建一个扩展的实例，然后传递应用对象作为参数进行初始化的。当应用对象没有以全局变量的形式存在，那么扩展就可以通过两个步骤进行初始化。扩展首先以全局变量的形式被创建，但是不会传递任何参数。这会创建一个扩展的实例但是并没有绑定到应用上。当应用在工厂函数中被创建的时候，`init_app()` 方法必须被调用让扩展绑定到当前的应用实例上。

其他的初始化任务保持不变，但是被移动到了工厂函数里。包括了蓝图的注册以及日志的配置。注意到我添加了一个 `not app.testing` 条件子句来决定 email 和文件日志是否被激活，这样在测试中的日志都会被跳过。`app.testing` 标志在运行单元测试的时候为 `True`，由于配置中的 `TESTING` 变量被设置成了 `True`。

那么谁来调用应用工厂函数呢？明显的地方是在顶层 `microblog.py` 脚本中调用，它是目前全局变量的应用对象唯一存在的地方。另外的地方是在 `tests.py`，在下一节我会详细的讨论单元测试。

现在大多数对 `app` 的引用都转移到了蓝图中，但是仍然还有一些代码会使用 app 对象。比如，`app/models.py`，`app/translate.py` 和 `app/main/routes.py` 模块都引用了 `app.config`。幸运的是，Flask 开发者已经提供了如何在视图函数中更加方便的使用应用实例而不用像现在我这样去导入它。Flask 中提供的 `current_app` 是一个特别的上下文变量。你已经看到了其他上下文变量，比如用于存储当前语言的 `g` 变量。这两个以及 Flask-Login 的 `current_user` 和其他你没有见过的变量，是所谓的魔法变量，虽然是以全局变量的形式工作的，但是只有在处理一个请求的时候才可用，并且只有在处理该请求的线程中可以获取。

将 app 替换为 Flask 的 `current_app` 变量消除了将应用实例作为全局变量进行导入。我可以通过简单的搜索和替换将所有的 `app.config` 引用变成 `current_app.config`。

`app/email.py` 有一点挑战，所以我使用了一点小技巧

```python
from app import current_app

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()
```

在 `send_email()` 函数中，应用实例被作为参数传入后台线程，之后会发送电子邮件但是不会阻塞主应用。直接在 `send_async_email()` 函数使用 `current_app` 作为后台线程运行不会成功，因为 `current_app` 是上下文变量，需要绑定到一个处理客户端请求的线程上。在其他线程中，`current_app` 则没有被赋值。直接向线程对象中传递 `current_app` 参数也不可以，因为 `current_app` 其实是一个动态生成应用实例的代理对象。因此直接传递一个代理对象就和在函数中直接使用 `current_app` 一样不会成功。我需要做的是提取出代理对象中实际的应用实例，然后作为 `app` 参数传递进去。`current_app._get_current_object()` 表达式从代理对象中提取出了实际的应用实例，所以这就是我作为参数传递到线程的对象。

另外一个比较棘手的模块是 `app/cli.py`，其实现了一些操作语言翻译的快捷命令。`current_app` 对象不能在这里工作的原因是这些命令在启动的时候注册，而不是在处理请求的时候。为了移除这个模块的 `app` 引用，我使用了另一个技巧，是将这些自定义命令放入一个 `register()` 函数中，该函数接收 `app` 实例作为参数：

```python
import os
import click

def register(app):
    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language."""
        # ...

    @translate.command()
    def update():
        """Update all languages."""
        # ...

    @translate.command()
    def compile():
        """Compile all languages."""
        # ...
```

然后在 `microblog.py` 中调用 `register()` 函数，下面是重构之后完整的 `microblog.py`

```python
from app import create_app, db, cli
from app.models import User, Post

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post' :Post}
```

改进单元测试
===

正如我在本章开始时候暗示的一样，目前已经做了很多工作可以用于提升单元测试。当你运行单元测试的时候你想确保你的应用被配置正确而不会影响你的开发环境，比如数据库。

当前版本的 `tests.py` 是使用了在配置已经应用到应用实例上之后改变其配置的技巧，但是这样做比较危险，因为不是所有类型的改变在这之后会生效。我想要的是在我将配置添加到应用之前指定为测试环境配置。

`create_app()` 函数现在接收一个配置类作为参数。默认，使用在 `config.py` 中定义的 `Config` 类，现在我可以创建使用不同配置的应用实例，只需要将不同的配置类传递给工厂函数。下面是一个跟我的单元测试匹配的配置类。

```python
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
```

这里我们创建了 `Config` 类的子类，然后重写了 SQLAlchemy 配置以使用内存 SQLite 数据库。我同样将 `TESTING` 属性设置为 True，当然现在不需要，但是如果应用需要辨别现在是在运行单元测试还是其他什么的时候很有用。

回忆一下，我的单元测试依赖于 `SetUp()` 和 `tearDown()` 方法，被单元测试框架自动的调用以创建和销毁适合每个单元测试运行的环境。我可以通过这两个方法来为每个测试创建或者销毁一个新的应用实例。

```python
class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
```

新的应用会在 `self.app` 中存储，但是单纯创建一个应用并不能让测试正常工作。考虑 `db.create_all()` 语句，db 实例需要知道当前的应用实例是什么，因为它需要从 `app.config` 中获取数据库 URI，但是当你使用应用工厂的时候可以创建多个应用。那么 db 如何才能知道使用 `self.app` 实例呢？

答案就是应用上下文。还记得 `current_app` 变量么，当没有全局变量导入的时候它是应用代理。这个变量会在当前线程中寻找一个激活的应用上下文，如果找到，它会从中获取应用实例。如果没有上下文存在，那么就没办法知道哪个应用是活动的，所以 `current_app` 会引发一个异常。在下面你可以看到如何在一个 Python 控制台进行工作的。这需要通过 python 来启动控制台，因为 `flask shell` 命令会为当前会话自动激活一个应用上下文。

```
>>> from flask import current_app
>>> current_app.config['SQLALCHEMY_DATABASE_URI']
Traceback (most recent call last):
    ...
RuntimeError: Working outside of application context.

>>> from app import create_app
>>> app = create_app()
>>> app.app_context().push()
>>> current_app.config['SQLALCHEMY_DATABASE_URI']
'sqlite:////home/miguel/microblog/app.db'
```

这就是秘诀所在！在调用你的视图函数之前，Flask 会进行上下文入栈，这样会激活 `current_app` 和 `g`。当请求完成之后，上下文就被移除了，同时这些变量也被销毁了。为了 `db.create_all()` 调用可以在 `setUp()` 方法中运行，我将刚才创建的应用上下文入栈，这样，`db.create_all()` 就可以使用 `current_app.config` 得到数据库地址。然后在 `tearDown()` 方法中将上下文移除，并且将相关的状态清理。

你也应该知道应用上下文是 Flask 使用的两种上下文之一。还有一个请求上下文，更加确切的是应用在一个请求之上的。在一个请求被处理之前请求上下文会被激活，Flask 的 request 和 session 变量就可以使用了，以及 Flask-Login 的 `current_user`.

环境变量
===

该应用有好几个配置项是依赖于在服务器启动之前设置的环境变量。包括你的密钥(secret key)，电子邮件服务器信息，数据库 URL 以及微软的翻译器 API key。你可能觉得这不方便，因为每次打开新的终端都需要重新设置一遍环境变量。

这种需要多个环境变量变量的应用一种通用的模式是将环境变量存储在一个 `.env` 文件里。应用在启动之前读取这个文件的变量，这样就不必每次都手动设置了。

有一个支持 `.env` 文件的包，叫做 `python-dotenv`，首先让我们安装这个包

```shell
(venv) $ pip install python-dotenv
```

因为我在 `config.py` 模块中读取了所有的环境变量，因此我将在这里导入 `.env` 文件，并且是在 `Config` 类被创建之前，因此在该类被构建的时候那些环境变量就已经设置好了。

```python
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    # ...
```

现在你就可以创建一个应用所有需要的环境变量的 `.env` 文件。最重要的一点是不要将 `.env` 文件加入到源代码控制中。你不会希望一个包含密码和其他敏感信息的文件包含在代码仓库里的。

`.env` 文件不可以用作 Flask 的 `FLASK_APP` 和 `FLASK_DEBUG` 环境变量，因为这些需要在应用的引导程序中，在应用实例和配置对象存在之前读取。

下面是一个 `.env` 文件的例子。

```python
SECRET_KEY=a-really-long-and-unique-key-that-nobody-knows
MAIL_SERVER=localhost
MAIL_PORT=25
MS_TRANSLATOR_KEY=<your-translator-key-here>
```

依赖文件
===

到目前为止，我已经在 Python 虚拟环境中安装了许多包。如果你需要在其他机器上重新生成你的环境，你需要知道你现在安装了什么包。所以一般是在根目录下的 `requirements.txt` 文件中记下所有需要的依赖以及版本。列出这些依赖也很简单：

```shell
(venv) $ pip freeze > requirements.txt
```

`pip freeze` 命令会将所有安装的包以`requirements.txt` 要求的格式输出。现在如果你需要在其他机器上创建一个相同的虚拟环境，不需要一个个装依赖，只需要：

```shell
(venv) $ pip install -r requirements.txt
```
