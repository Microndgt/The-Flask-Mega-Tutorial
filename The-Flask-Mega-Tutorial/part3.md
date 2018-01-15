The Flask Mega-Tutorial Part III: Web Forms
===

原文地址: [The Flask Mega-Tutorial Part III: Web Forms](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms)

这是Flask Mega-Tutorial系列的第三部分，我将带你学习web表单(forms)

在第二部分，我为应用首页创建了一个简单的模板，而且使用了模拟对象作为目前还没有的东西的替代品，比如用户或者文章对象。在这章我将要解决的是目前应用存在的诸多问题之一，如何通过web表单来接受用户的输入。

Web表单是任何web应用中最基本的组成构件之一。我将使用表单来允许用户提交文章以及登录应用。

在开始这章之前，确保你已经拥有上一章完成的应用，并且运行没有错误。

本章的Github链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.3), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.3.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.2...v0.3)

Flask-WTF简介
===

为了处理应用中的web表单，我使用了[Flask-WTF](http://packages.python.org/Flask-WTF)扩展，它是对[WTForms](https://wtforms.readthedocs.io/)的简单封装并与Flask很好的整合在一起。这是我向你展示的第一个Flask扩展，但不是最后一个。在Flask生态系统中，扩展是非常重要的一部分，它们提供了Flask有意没有处理的问题的解决方案。

Flask扩展也是普通的Python包，可以使用pip来安装。你可以用以下命令在虚拟环境中安装`Flask-WTF`: `pip install flask-wtf`

配置
===

因为现在应用很简单，因此我不需要担心它的配置问题。但是对于除过这个最简单的其他任何应用来说，你将发现Flask(以及你使用的Flask扩展)会提供一定的自由度，你需要来向框架传递一个配置变量的列表来决定怎么做。

应用有几种指定配置选项的格式。最基本的是以`app.config`的键(key)的形式定义变量，它使用了字典的风格来定义变量。比如，你可以这样：

```
app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
# ... add more variables here as needed
```

虽然上面的方式已经足够来为Flask创建配置选项，但是我更乐意去实现关注点分离原则(the principle of separation of concerns)，所以与其将我的配置和创建应用放在一起，不如我使用一个稍微复杂的结构来将我的配置文件放在单独的文件里。

我非常喜欢使用一个类来储存配置，是因为它非常容易扩展。为了更好的组织，我将会在一个单独的Python模块中创建这个配置类。下面你可以看到为应用创建的新的配置类，存储在顶层目录的`config.py`模块中。

```
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
```

非常简单对吧？配置现在是以类属性的方式定义在`Config`类中的。如果应用需要更多的配置项，那么可以继续添加到类中。如果后面我需要再创建配置集合，我可以创建`Config`的子类。但是目前先不用考虑它。

目前唯一配置的`SECRET_KEY`配置变量在大多数Flask应用中都是非常重要的一部分。Flask和其他一些扩展会使用这个值作为加密密钥用于生成签名或者令牌。Flask-WTF使用它来保护web表单免于[Cross-Site Request Forgery](http://en.wikipedia.org/wiki/Cross-site_request_forgery) - CSRF的攻击(发音为seasurf)。顾名思义，secret key应该是私密的，其生成的令牌和签名的安全程度取决于除了应用的维护者之外没有人知道。

这个值的赋值语句分为两部分，通过`or`操作符连接在一起。第一部分是查找一个也叫作`SECRET_KEY`的环境变量。第二部分，是一个硬编码字符串。这种模式在后面很多配置赋值的时候都会用到，首先去读取环境变量的值，如果没有，则使用硬编码字符串作为替代。当你开发这个应用的时候，没有太高的安全需求，所以你可以直接使用这个硬编码字符串。但是如果应用部署在生产服务器上，我将会在环境变量中设置相应的值以保证安全。

现在我已经有了配置文件，我需要告知Flask读取并且应用配置。这可以通过使用`app.config.from_object()`方法来完成：

```
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes
```

上面`config`是Python模块，而`Config`(uppercase "C")是这个Python模块中的类。

正如我上面提到的，配置项可以使用字典语法来从`app.config`读取。下面展示了我如何读取secret key的：

```
>>> from microblog import app
>>> app.config['SECRET_KEY']
'you-will-never-guess'
```

用户登陆表单
===

Flask-WTF扩展使用Python类来表达web表单。表单类简单的使用类变量代表表单字段。

再一次牢记关注点分离，我将会使用一个新的`app/forms.py`模块来存储我的表单类。作为开始，我们先定义一个用户登陆表单，用来请求用户输入用户名和密码。表单还会包含一个`remember me`的选择框和一个提交按钮：

```
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
```

大多数Flask扩展会使用`flask_<name>`的命名传统作为它们顶层的导入符号。在这个例子中，Flask-WTF使用了`flask_wtf`。在`app/form.py`顶部，FlaskForm基类就是从这导入的。

因为Flask-WTF扩展没有提供自定义的版本，所以下面的四个类是我直接从WTForms包导入的，用来表示字段类型。在LoginForm类中，对于每一个字段都会创建相应的对象并且赋值给LoginForm类的一个类变量。每个字段都会将描述或者标签作为第一个参数。

可选的`validators`参数是用来给字段附加验证行为的。`DataRequired`验证器简单的检查提交的字段是不是为空。还有很多可用的验证器，可以用到其他的一些表单上。

表单模板
===

下一步就是将表单加入到HTML模板中，这样就可以被渲染为一个web页面了。好消息是在`LoginForm`类中定义的字段知道如果将自己渲染为HTML，因此这项工作非常简单。下面你可以看到一个登陆模板，这个文件存储在`app/tempaltes/login.html`

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

这个模板中我再次通过`extends`模板继承语句使用了在第二节中展示的`base.html`。我将会在所有模板中使用继承，以确保在应用的所有页面顶部都可以包含一个导航栏。

这个模板需要一个LoginForm类的实例作为参数，即你看到的form。这个参数会被login视图函数传入，但是目前还没有完成这个函数。

HTML的`<form>`元素用来承载web表单。表单的`action`属性用来告诉浏览器在用户点击提交信息的时候使用这个URL。如果action为空，则表单会提交到当前地址栏的URL，也就是渲染当前页面表单的URL。`method`属性表示当提交表单到服务器的时候应该使用什么HTTP方法。默认是发送一个`GET`请求，但是在大多数情况下会使用POST请求，因为POST请求可以在请求体中包含表单数据，而GET请求会将form字段放到URL中，这样搞得地址栏乱糟糟的，体验很不好。

`form.hidden_tag()`会生成一个用来保护表单免受CSRF攻击的令牌。为了保护表单，你需要做的只是在表单中包含这个隐藏字段以及在Flask配置中定义`SECRET_KEY`变量。如果你做好了这两件事，剩下的就交给Flask-WTF吧。

如果你之前写过HTML web表单，你可能会觉得在模板中没有HTML字段会很奇怪。这是因为form对象的字段知道如何将自己渲染为HTML。所有我需要做的是，如果需要字段名，则使用`{{ form.<field_name>.label }}`；如果需要字段，则使用`{{ form.<field_name>() }}`。对于字段可能需要传递额外的参数作为HTML属性。模板中的username和password两个字段使用的`size`参数将会作为属性加入到`<input>`元素中。而且你也可以在这里给表单字段附加CSS classes或者IDs。

表单视图
===

在你能看到表单之前，只剩最后一步——在应用中添加一个新的视图函数，用来渲染上一节的模板。

因此让我们来创建一个映射`/login` URL的视图函数吧。这个函数会创建一个form对象，然后传递给模板用来渲染。这个视图函数依然可以定义在`app/routes.py`模块里。

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

这里我从`forms.py`导入了LoginForm类，并且实例化了一个对象，将其送到模板中。`form=form`语法看起来很奇怪，但是仅仅是将form对象传递到了模板中。这就是渲染表单字段所有需要做的事情。

为了能够容易的进入登录表单，可以在base模板中的导航栏中添加一个链接：

```
<div>
    Microblog:
    <a href="/index">Home</a>
    <a href="/login">Login</a>
</div>
```

这时候你就可以运行应用程序并且可以在浏览器中看到表单了。在浏览器地址栏输入`http://localhost:5000/`然后在顶部导航栏中点击`Login`链接就可以看到登录表单了，是不是很酷？

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch03-login-form.png)