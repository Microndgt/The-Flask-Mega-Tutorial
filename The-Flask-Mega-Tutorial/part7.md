The Flask Mega-Tutorial Part VII: Error Handling
===

原文地址: [The Flask Mega-Tutorial Part VII: Error Handling](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-error-handling)

在这章我将不会在我的博客应用中添加新的功能了，而是我会讨论下关于如何处理 bug 的策略，这是任何软件工程必须要面对的事情。为了详细说明这一主题，在第 6 章中我特意留下了一个 bug。在你阅读之前，看看你是否能找到这个 bug！

本章的 Github 链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.7), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.7.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.6...v0.7)

Flask 中的错误处理
===

在 Flask 应用中出现错误会发生什么？最好的方式就是体验一下。启动应用，并且确保你有两个注册用户。登录其中一个用户，打开个人资料页面，然后点击 `Edit` 链接。在个人资料编辑器中，尝试修改用户名为另一个注册用户的用户名，嘣！出现了一个 `Internal Server Error` 页面：

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch07-500-error.png)

如果你查看应用运行的终端，你就会发现一个错误堆栈。在 debug 错误的时候，错误堆栈非常有用，因为它显示了调用的系列过程，直到发生了错误：

```shell
(venv) $ flask run
 * Serving Flask app "microblog"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
[2017-09-14 22:40:02,027] ERROR in app: Exception on /edit_profile [POST]
Traceback (most recent call last):
  File "/home/miguel/microblog/venv/lib/python3.6/site-packages/sqlalchemy/engine/base.py", line 1182, in _execute_context
    context)
  File "/home/miguel/microblog/venv/lib/python3.6/site-packages/sqlalchemy/engine/default.py", line 470, in do_execute
    cursor.execute(statement, parameters)
sqlite3.IntegrityError: UNIQUE constraint failed: user.username
```

堆栈指明了发生了什么错误。应用允许用户修改用户名，但是并没有验证新的用户名是否与系统已有的用户名冲突。这是从 SQLAlchemy 引发的错误，尝试向数据库中写入一个新的用户名，但是因为 `username` 字段是 `unique` 的，所以这一写入操作被拒绝执行。

值得注意的是这个错误页面并没有给用户提供太多有用的信息，这是应该的。因为我不想让用户知道这个错误是因为数据库引起的以及我使用了什么数据库，抑或我使用了什么表和什么字段。所有这些信息都应该是内部信息。

但是这些都离理想状况很远。错误页面很丑而且没有适配应用已有的布局。而且非常重要的错误堆栈信息打印到了终端上，所以我不得不盯着终端以防错过了错误信息。当然我有一个 bug 需要处理，但是首先让我们先来了解下 Flask 的 debug 模式。

调试模式
===

上面展示的错误处理方式对于在生产环境运行的服务器是不错的，因为如果有错误的话，用户将会得到一个模糊的错误页面(当然我可以使得这个页面更好看些)，然后错误详情会输出到一个 log 文件里。

但是当你在开发应用的时候，你可以开启 debug 模式，这个模式会使得 Flask 直接在你的浏览器上输出一个很友好的调试器。为了开启 debug 模式，停止应用，然后设置以下的环境变量：

```shell
(venv) $ export FLASK_DEBUG=1
```

如果你使用的是 Windows，记得使用 `set` 而不是 `export`

在你设置完 `FLASK_DEBUG`之后，重启服务器。这样终端上输出的就和以前稍微不一样了。

```shell
(venv) microblog2 $ flask run
* Serving Flask app "microblog"
* Forcing debug mode on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 177-562-960
```

那么现在再让程序崩溃一次，然后看看浏览器上会出现什么：

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch07-debugger.png)

调试器允许你展开每一个堆栈层，然后查看相应的源代码。而且你还可以在任意一层中打开一个 Python 提示符，并且执行有效的 Python 语句，比如查看变量的值。

非常重要的是，坚决不能在生产环境中打开 debug 模式。调试器会允许用户在服务器上远程执行代码，所以一些恶意用户就有可能凭借此渗透你的应用或者服务器。作为额外的安全措施，在浏览器上的调试器一开始是锁定的，你必须输入一个 PIN 码，在 `flask run` 命令的输出里你可以看到这个码。

第二个关于 debug 模式的重要特性就是 reloader。这是一个非常有用的功能，当你修改代码之后，应用就是自动重启。当你在 debug 模式启动 `flask run`的时候，你可以在任何时候保存文件之后看到效果，应用会自动重启应用新的代码。

自定义错误页面
===

Flask 提供让应用自定义其错误页面的机制，这样你就不需要总是看到那些普通乏味的默认页面。作为示例，我们自定义 404 和 500 错误页面，这是最常出现的两个页面。定义其他错误页面也是同样的道理。

为了声明一个自定义的错误处理器，会使用到 `@errorhandler` 装饰器。我会将错误处理器放在 `app/errors.py` 模块中。

```python
from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
```

错误处理函数和视图函数很像。对于这两个错误，分别返回了它们对应的模板。注意到每个函数都额外返回了一个错误码。对于目前创建的所有视图函数来说，我并不需要添加第二个返回值，因为默认都是 200 (表示是成功的响应)。在这个例子中，因为都是错误页面，因此我会返回错误对应的状态码。

500 错误的处理器可能会在数据库错误之后被调用，比如重复的用户名。为了确保失败的数据库事务不会影响其他的数据库访问，因此进行了事务回滚。这样就会使得这次事务返回原始状态。

下面是 404 错误的模板：

```html
{% extends "base.html" %}

{% block content %}
    <h1>File Not Found</h1>
    <p><a href="{{ url_for('index') }}">Back</a></p>
{% endblock %}
```

下面是 500 错误的模板：

```html
{% extends "base.html" %}

{% block content %}
    <h1>An unexpected error has occurred</h1>
    <p>The administrator has been notified. Sorry for the inconvenience!</p>
    <p><a href="{{ url_for('index') }}">Back</a></p>
{% endblock %}
```

两个模板都是继承于 `base.html` 模板，因此这两个错误页面和其他正常页面有着同样的外观。

为了在 Flask 注册这几个错误处理器，我需要在应用实例创建之后导入这个 `app/errors.py` 模块

```python
# ...

from app import routes, models, errors
```

如果你在终端中设置了 `FLASK_DEBUG = 0`， 然后再触发之前的错误，你就会看到一个更友好的错误页面：

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch07-500-custom.png)

通过 Email 发送错误
===

对于 Flask 的默认错误处理还有一个问题就是没有提醒功能，错误堆栈是打印在终端上的，也就意味着服务器处理程序的输出必须被监控来发现错误。如果在开发环境上，这样是可以的，但是如果部署到生产服务器上的话，没有人会去看输出，因此需要一个更健壮的解决办法。

我认为对于错误应该采取更主动的处理方式。如果应用的生产版本上发生了错误，那么我应该立即知道。因此我第一个办法就是在发生错误之后，立马发送一封有着错误堆栈信息的邮件给我自己。

首先是在配置文件中添加 email 服务器信息：

```python
class Config(object):
    # ...
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
```

配置变量包括了邮件服务器和端口，布尔标志来指示加密链接，可选的用户名和密码。这些配置变量来自于对应的环境变量。如果没有设置邮件服务器变量，我就会使用这个作为禁止错误邮件提醒功能的标志。邮件服务器端口也可以以环境变量的方式给定，如果没有设置，那么就是使用默认的 25 端口。邮件服务器认证默认是不适用的，如果需要的话可以提供。`ADMINS` 配置变量提供了一系列的邮件地址，将会收到错误报告，因此你自己的邮件地址应该包含在内。

Flask 使用了 Python 的 `logging` 包来输出日志，而且这个包已经有了通过邮箱发送日志的功能。我需要做的是向 Flask logger 对象添加一个 [SMTPHandler](https://docs.python.org/3.6/library/logging.handlers.html#smtphandler) 实例：

```python
import logging
from logging.handlers import SMTPHandler

# ...

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
```

正如你看到的，只有在非 debug 模式下我才会发送邮件，当然也必须在指定邮件服务器的情况下。

配置邮件日志有时候是乏味的，因为需要处理出现在大部分服务器的额外安全选项。但是本质上，上面代码创建了一个 `SMTPHandler` 实例，并且只会报告错误日志，最后将其附到 Flask 的 `app.logger` 对象上。

有两种方法来测试这个功能，最简单的是使用 Python 的 SMTP 调试服务器。这是一个可以接受邮件的模拟邮件服务器，相反不是发送邮件，而是直接打印到控制台上。为了运行这个服务器，打开第二个终端，然后输入以下命令：

```shell
(venv) $ python -m smtpd -n -c DebuggingServer localhost:8025
```

为了在这个服务器上测试应用，你要设置 `MAIL_SERVER=localhost` 和 `MAIL_PORT=8025`。如果你在 Linux 或者 Mac OS 上，你可能需要使用 `sudo` 作为命令前缀，这样就可以以管理员权限运行命令了。如果你在 Windows 上，你可能需要以管理员权限打开终端。之所以需要管理员权限是因为低于 1024 的端口是管理员端口。可选的，你可以设置更高数字的端口比如 5025，然后在环境变量中设置 `MAIL_PORT` 变量，这样就不会需要管理员权限。

让调试 SMTP 服务器运行，然后返回第一个终端，设置 `export MAIL_SERVER=localhost` 和 `MAIL_PORT=8025`。确保 `FLASK_DEBUG` 变量设置为 0，或者不设置，因为应用不会在 debug 模式下发送邮件。运行应用，然后触发 SQLAlchemy 错误，然后查看终端，你可以看到模拟邮件服务器显示了一个有着错误堆栈信息的邮件。

另一个测试方法是配置一个真实的邮件服务器，下面是一个使用了 Gmail 服务器的配置：

```shell
export MAIL_SERVER=smtp.googlemail.com
export MAIL_PORT=587
export MAIL_USE_TLS=1
export MAIL_USERNAME=<your-gmail-username>
export MAIL_PASSWORD=<your-gmail-password>
```

由于 Gmail 的安全措施，你的邮件可能不能发送成功，除非你显式的允许你的 Gmail 账户开启 "less secure apps"。

输出日志到文件
===

通过邮件来接受错误，这种方式不错，但是有时候还不够。因为有一些失败的情况可能没有在一个 Python 异常中结束，而且可能不是一个大问题，但是如果存储下来为了调试目的来说还挺有趣。基于上述原因，我同样会为应用维护一个日志文件。

为了开启一个基于文件的日志处理器，这次我用 [RotatingFileHandler](https://docs.python.org/3.6/library/logging.handlers.html#rotatingfilehandler)，需要附到应用的 logger 上，和上面邮件处理器一样。

```python
# ...
from logging.handlers import RotatingFileHandler
import os

# ...

if not app.debug:
    # ...

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
```

我将日志文件命名为 `microblog.log`，存储在 logs 目录下，并且在不存在的情况下创建这个目录。

`RotatingFileHandler` 这个类可以确保日志文件不会因为长时间运行应用变的特别大，我设置了最大日志文件为 10KB，然后会保持最近的 10 个文件。

`logging.Formatter` 提供了日志消息的自定义格式。因为这些文件要写入到一个文件里，因此我尽可能多的包含信息。因此我自定义了一个包含时间戳，日志等级，消息以及源文件路径和行数的信息格式。

为了让日志更加有用，我将文件和应用日志等级都降低到了 `INFO`。可能你对日志等级还不熟悉，以严重程度增长排序有以下等级：`DEBUG`, `INFO`, `WARNING`, `ERROR` 和 `CRITICAL`。

后面会输出一条消息用于表示应用已经启动了，如果在生产服务器上，这条消息可以作为服务器重启的标志。

修复用户名重复的 Bug
===

这个用户名重复的 bug 已经存在太久了，是时候修复它了。我会向你展示如何准备应用来处理这种错误。

回忆下，`RegistrationForm` 已经实现了用户名验证，但是编辑表单的需求会有些许不同。在注册中，我需要确保用户在表单上输入的用户名不会和数据库中重复。在编辑资料表单中我也要做同样的检测。如果用户没有改变用户名，那么验证通过。下面你可以看到为这个表单实现的用户名验证：

```python
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
```

是在一个自定义验证方法中实现了验证功能，但是重载了接收一个原始用户名的构造器。这个用户名被存储为实例变量，并且会在验证方法中检测是否和输入的用户名一致，如果一致，就不需要检测。

为了使用这个新的验证方法，我需要在表单对象创建的时候将原始用户名作为参数传递进来：

```python
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # ...
```

这样 bug 就被修复了，但是这不是一个完美的解决方案，因为如果有两个或者更多的进程同时读取数据库的时候就会有问题。这种情况下，竞争条件可能会导致验证通过，但是另一个进程已经修改了用户名，就会导致冲突。
