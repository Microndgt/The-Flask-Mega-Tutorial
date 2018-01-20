The Flask Mega-Tutorial Part III: Web Forms
===

原文地址: [The Flask Mega-Tutorial Part III: Web Forms](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms)

这是 Flask Mega-Tutorial 系列的第三部分，我将带你学习 web 表单(forms)

在第二部分，我为应用首页创建了一个简单的模板，而且使用了模拟对象作为目前还没有的东西的替代品，比如用户或者文章对象。在这章我将要解决的是目前应用存在的诸多问题之一，如何通过 web 表单来接受用户的输入。

Web 表单是任何 web 应用中最基本的组成构件之一。我将使用表单来允许用户提交文章以及登录应用。

在开始这章之前，确保你已经拥有上一章完成的应用，并且运行没有错误。

本章的 Github 链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.3), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.3.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.2...v0.3)

Flask-WTF 简介
===

为了处理应用中的 web 表单，我使用了[Flask-WTF](http://packages.python.org/Flask-WTF)扩展，它是对[WTForms](https://wtforms.readthedocs.io/)的简单封装并与 Flask 很好的整合在一起。这是我向你展示的第一个 Flask 扩展，但不是最后一个。在 Flask 生态系统中，扩展是非常重要的一部分，它们提供了 Flask 有意没有处理的问题的解决方案。

Flask 扩展也是普通的 Python 包，可以使用 pip 来安装。你可以用以下命令在虚拟环境中安装`Flask-WTF`: `pip install flask-wtf`

配置
===

因为现在应用很简单，因此我不需要担心它的配置问题。但是对于除过这个最简单的其他任何应用来说，你将发现 Flask (以及你使用的 Flask 扩展)会提供一定的自由度，你需要来向框架传递一个配置变量的列表来决定怎么做。

应用有几种指定配置选项的格式。最基本的是以 `app.config` 的键(key)的形式定义变量，它使用了字典的风格来定义变量。比如，你可以这样：

```python
app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
# ... add more variables here as needed
```

虽然上面的方式已经足够来为 Flask 创建配置选项，但是我更乐意去实现关注点分离原则(the principle of separation of concerns)，所以与其将我的配置和创建应用放在一起，不如我使用一个稍微复杂的结构来将我的配置文件放在单独的文件里。

我非常喜欢使用一个类来储存配置，是因为它非常容易扩展。为了更好的组织，我将会在一个单独的 Python 模块中创建这个配置类。下面你可以看到为应用创建的新的配置类，存储在顶层目录的 `config.py` 模块中。

```python
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
```

非常简单对吧？配置现在是以类属性的方式定义在 `Config` 类中的。如果应用需要更多的配置项，那么可以继续添加到类中。如果后面我需要再创建配置集合，我可以创建 `Config` 的子类。但是目前先不用考虑它。

目前唯一配置的 `SECRET_KEY` 配置变量在大多数 Flask 应用中都是非常重要的一部分。Flask 和其他一些扩展会使用这个值作为加密密钥用于生成签名或者令牌。Flask-WTF 使用它来保护 web 表单免于[Cross-Site Request Forgery](http://en.wikipedia.org/wiki/Cross-site_request_forgery) - CSRF 的攻击(发音为 seasurf)。顾名思义，secret key 应该是私密的，其生成的令牌和签名的安全程度取决于除了应用的维护者之外没有人知道。

这个值的赋值语句分为两部分，通过 `or` 操作符连接在一起。第一部分是查找一个也叫作 `SECRET_KEY` 的环境变量。第二部分，是一个硬编码字符串。这种模式在后面很多配置赋值的时候都会用到，首先去读取环境变量的值，如果没有，则使用硬编码字符串作为替代。当你开发这个应用的时候，没有太高的安全需求，所以你可以直接使用这个硬编码字符串。但是如果应用部署在生产服务器上，我将会在环境变量中设置相应的值以保证安全。

现在我已经有了配置文件，我需要告知 Flask 读取并且应用配置。这可以通过使用 `app.config.from_object()` 方法来完成：

```python
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes
```

上面 `config` 是 Python 模块，而 `Config`(uppercase "C") 是这个 Python 模块中的类。

正如我上面提到的，配置项可以使用字典语法来从 `app.config` 读取。下面展示了我如何读取 secret key 的：

```shell
>>> from microblog import app
>>> app.config['SECRET_KEY']
'you-will-never-guess'
```

用户登陆表单
===

Flask-WTF 扩展使用 Python 类来表达 web 表单。表单类简单的使用类变量代表表单字段。

再一次牢记关注点分离，我将会使用一个新的 `app/forms.py` 模块来存储我的表单类。作为开始，我们先定义一个用户登陆表单，用来请求用户输入用户名和密码。表单还会包含一个 `remember me` 的选择框和一个提交按钮：

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
```

大多数 Flask 扩展会使用 `flask_<name>` 的命名传统作为它们顶层的导入符号。在这个例子中，Flask-WTF 使用了 `flask_wtf`。在 `app/form.py` 顶部，FlaskForm 基类就是从这导入的。

因为 Flask-WTF 扩展没有提供自定义的版本，所以下面的四个类是我直接从 WTForms 包导入的，用来表示字段类型。在 LoginForm 类中，对于每一个字段都会创建相应的对象并且赋值给 LoginForm 类的一个类变量。每个字段都会将描述或者标签作为第一个参数。

可选的 `validators` 参数是用来给字段附加验证行为的。 `DataRequired` 验证器简单的检查提交的字段是不是为空。还有很多可用的验证器，可以用到其他的一些表单上。

表单模板
===

下一步就是将表单加入到 HTML 模板中，这样就可以被渲染为一个 web 页面了。好消息是在 `LoginForm` 类中定义的字段知道如果将自己渲染为 HTML，因此这项工作非常简单。下面你可以看到一个登陆模板，这个文件存储在 `app/tempaltes/login.html`

```
{% extends "base.html" %}

{% block content %}
    <h1>Sign In</h1>
    <form action="" method="post">
        {{ form.hidden_tag() }}
        <p>
            {{ form.username.label }}<br>
            {{ form.username(size=32) }}
        </p>
        <p>
            {{ form.password.label }}<br>
            {{ form.password(size=32) }}
        </p>
        <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
```

这个模板中我再次通过 `extends` 模板继承语句使用了在第二节中展示的 `base.html`。我将会在所有模板中使用继承，以确保在应用的所有页面顶部都可以包含一个导航栏。

这个模板需要一个 LoginForm 类的实例作为参数，即你看到的 form。这个参数会被 login 视图函数传入，但是目前还没有完成这个函数。

HTML 的 `<form>` 元素用来承载 web 表单。表单的 `action` 属性用来告诉浏览器在用户点击提交信息的时候使用这个 URL。如果 action 为空，则表单会提交到当前地址栏的 URL，也就是渲染当前页面表单的 URL。`method` 属性表示当提交表单到服务器的时候应该使用什么 HTTP 方法。默认是发送一个 `GET` 请求，但是在大多数情况下会使用 POST 请求，因为 POST 请求可以在请求体中包含表单数据，而 GET 请求会将 form 字段放到 URL 中，这样搞得地址栏乱糟糟的，体验很不好。

`form.hidden_tag()` 会生成一个用来保护表单免受 CSRF 攻击的令牌。为了保护表单，你需要做的只是在表单中包含这个隐藏字段以及在 Flask 配置中定义 `SECRET_KEY` 变量。如果你做好了这两件事，剩下的就交给 Flask-WTF 吧。

如果你之前写过 HTML web 表单，你可能会觉得在模板中没有 HTML 字段会很奇怪。这是因为 form 对象的字段知道如何将自己渲染为HTML。所有我需要做的是，如果需要字段名，则使用 `{{ form.<field_name>.label }}`；如果需要字段，则使用 `{{ form.<field_name>() }}`。对于字段可能需要传递额外的参数作为 HTML 属性。模板中的 username 和 password 两个字段使用的 `size` 参数将会作为属性加入到 `<input>` 元素中。而且你也可以在这里给表单字段附加 CSS classes 或者 IDs。

表单视图
===

在你能看到表单之前，只剩最后一步——在应用中添加一个新的视图函数，用来渲染上一节的模板。

因此让我们来创建一个映射 `/login` URL 的视图函数吧。这个函数会创建一个 form 对象，然后传递给模板用来渲染。这个视图函数依然可以定义在 `app/routes.py` 模块里。

```
from flask import render_template
from app import app
from app.forms import LoginForm

# ...

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)
```

这里我从 `forms.py` 导入了 LoginForm 类，并且实例化了一个对象，将其送到模板中。`form=form` 语法看起来很奇怪，但是仅仅是将 form 对象传递到了模板中。这就是渲染表单字段所有需要做的事情。

为了能够容易的进入登录表单，可以在 base 模板中的导航栏中添加一个链接：

```
<div>
    Microblog:
    <a href="/index">Home</a>
    <a href="/login">Login</a>
</div>
```

这时候你就可以运行应用程序并且可以在浏览器中看到表单了。在浏览器地址栏输入 `http://localhost:5000/` 然后在顶部导航栏中点击 `Login` 链接就可以看到登录表单了，是不是很酷？

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch03-login-form.png)

接收表单数据
===

如果你按下提交按钮，浏览器将会显示 `Method Not Allowed` 的错误。这是因为之前的登录视图函数只完成了一半的工作。它可以在 web 页面上展示表单，但是还没有处理用户提交的数据的逻辑。这就是另外 Flask-WTF 会让工作变得容易的一部分。下面就是让视图函数可以接收并且处理用户提交数据的更新版本：

```python
from flask import render_template, flash, redirect

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)
```

在这个版本中第一个不同点是在路由装饰器中的 `methods` 参数。这声明了该视图函数可以接受 `GET` 和 `POST` 请求，默认只是 `GET` 请求。HTTP 协议使用 `GET` 请求来向客户端返回信息。目前这个应用的所有请求都是 `GET` 请求。`POST` 请求主要用在当浏览器要向服务器提交表单数据的时候(当然 `GET` 请求也可以用来提交，但是不推荐这么用)。浏览器显示的 `METHOD NOT ALLOWED` 错误是因为浏览器发送了一个该视图函数不能接收的 `POST` 请求。通过提供 `methods` 参数来告诉 Flask 这个请求方法应该被接收。

`form.validate_on_submit()` 方法解决了所有的表单处理工作。如果浏览器发送了 `GET` 请求需要接收一个有表单的 web 页面，这个方法就会返回 `False`，这样视图函数就会跳过 if 语句，直接执行最后一条语句来渲染页面返回。

当用户点击提交按钮之后，浏览器会发送一个 POST 请求，`form.validate_on_submit()` 将会收集所有数据，并且执行附加到各个表单字段上的验证方法，如果一切正常则会返回 True，表示数据有效并且可以被应用处理。只要有一个字段验证失败，这个方法就会返回 False，这样就会导致返回用户一个渲染的登录页面，就像 `GET` 请求发生的事情一样。后面我会在验证失败的时候加上错误消息。

当 `form.validate_on_submit()` 返回 True 的时候，登录视图函数会调用两个从 Flask 导入的函数。`flash()` 函数用来向用户展现一条消息。很多应用都用这项技术来向用户展示操作是否成功。在当前的情况下，我会使用这项技术作为临时的解决方案，因为我现在还没有拥有能够真实让用户登录成功的所有组件。现在我能够做的就是向用户展示消息来确认应用已经接受到了登录验证。

第二个用到的函数是 `redirect()`。这个函数会根据参数自动的引导浏览器前往相应页面。当前视图函数用它将用户重新引导到首页。

当你调用 `flash()` 函数的时候，Flask 存储了这条消息，但是消息并不会神奇的出现在 web 页面上。应用的模板需要来根据网页布局来渲染这些闪现消息。我将会在 base 模板上添加处理闪现消息的逻辑，这样所有模板都会继承这项功能。下面就是升级后的 base 模板：

```html
<html>
    <head>
        {% if title %}
        <title>{{ title }} - microblog</title>
        {% else %}
        <title>microblog</title>
        {% endif %}
    </head>
    <body>
        <div>
            Microblog:
            <a href="/index">Home</a>
            <a href="/login">Login</a>
        </div>
        <hr>
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <ul>
            {% for message in messages %}
            <li>{{ message }}</li>
            {% endfor %}
        </ul>
        {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </body>
</html>
```

这里我使用了 `with` 结构来将当前模板上下文中 `get_flashed_message()` 函数的调用结果赋值给 `messages` 变量。`get_flashed_message()` 来自于 Flask，会返回之前通过 `flash()` 函数注册的消息列表。后面紧跟着检查 `messages` 是否有值，每条消息作为一个 `<li>` 列表项包裹在 `<ul>` 元素中。虽然目前渲染的风格不是很好看，但是随后会开展关于应用风格的话题。

一个有趣的特性是这些闪现消息只要被 ``get_flashed_message()` 返回，就会从消息列表中移除，因此在 `flash()` 函数调用之后只会显示一次。

现在你就可以再次尝试启动应用并且来查看表单是怎么工作的。另外记得将用户名和密码字段置为空然后提交，这样你就可以看到 `DataRequired` 验证器是如何阻止了提交。

提升字段验证
===

绑定到表单字段上的验证器阻止了无效数据进入应用。应用处理无效数据表单输入的方式是重新展示表单输入，以让用户做出必要的修正。

如果你尝试提交无效数据，虽然验证机制工作正常，但是没有说明表单哪里出错的提示。下一步我们要加入的就是在验证失败的字段旁边添加上出错消息以提高用户体验。

事实上，这些表单验证器已经生成了描述性的错误消息，因此我们缺少的是在模板中渲染它们的额外逻辑。

下面就是一个在用户名和密码字段上添加了字段验证消息的登录模板：

```html
{% extends "base.html" %}

{% block content %}
    <h1>Sign In</h1>
    <form action="" method="post">
        {{ form.hidden_tag() }}
        <p>
            {{ form.username.label }}<br>
            {{ form.username(size=32) }}<br>
            {% for error in form.username.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>
            {{ form.password.label }}<br>
            {{ form.password(size=32) }}<br>
            {% for error in form.password.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
```

唯一的改变就是我在用户名和密码后面添加了一个读取并且以红色渲染错误消息的循环。一般而言，任何字段的验证器都会将错误消息添加在 `form.<field_name>.errors` 下。这些错误会是一个列表，因为可能字段会有多个验证器，所以可能会有多条错误消息。

如果你尝试以空的用户名或者密码提交，你将会看到红色的错误消息。

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch03-validation.png)

生成链接
===

登录表单现在已经基本完成，但是在结束本章之前，我想讨论关于如何合适的在模板和重定向中包含链接。目前你已经看到有一些定义了链接的实例。比如，下面是在 base 模板中的导航栏。

```html
<div>
    Microblog:
    <a href="/index">Home</a>
    <a href="/login">Login</a>
</div>
```

登录视图函数中同样定义了一个传递给 `redirect()` 函数的链接。

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # ...
        return redirect('/index')
    # ...
```

将链接直接写在模板或者源代码中的一个问题是如果将来你要重新组织你的链接，那么你就需要在整个应用中搜索并且替换所有的链接。

因此为了更好的控制这些链接，Flask 提供了一个叫做 `url_for()` 的函数，它会使用内部的 URL 到视图函数的映射来生成 URL。比如 `url_for('login')` 返回 `/login`，`url_for('index')` 返回 `/index`。传递给 `url_for()` 的参数是 endpoint 的名字，也就是视图函数的名字。

你可能会问为什么使用视图函数名字而不是 `URL`。是因为 URL 可能会经常变化，但是视图函数不会，因为视图函数只是内部使用的。第二个原因后面你将会学到，一些 URL 可能含有动态元素，因此自己来生成这些 URL 需要将多个元素组合在一起，不仅乏味而且易于出错。`url_for()` 函数同样可以处理这些复杂的 URL。

因此从现在开始，在需要生成应用 URL 的时候，我将使用 `url_for()` 。那么在 base 模板中的导航栏将变成下面这个样子：

```html
<div>
    Microblog:
    <a href="{{ url_for('index') }}">Home</a>
    <a href="{{ url_for('login') }}">Login</a>
</div>
```

这是更新后的 `login()` 视图函数

```python
from flask import render_template, flash, redirect, url_for

# ...

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # ...
        return redirect(url_for('index'))
```
