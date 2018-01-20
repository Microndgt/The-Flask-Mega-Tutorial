The Flask Mega-Tutorial Part II: Templates
===

原文地址: [The Flask Mega-Tutorial Part II: Templates](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates)

在 Flask Mega-Tutorial 系列的第二篇里，我将讨论如何使用模板。

在完成第一章之后，你应该有一个能完整工作，但是简单的 web 应用，它的结构是这样的：

```
microblog\
  venv\
  app\
    __init__.py
    routes.py
  microblog.py
```

为了运行这个应用，你需要在你的终端会话中设置 `FLASK_APP=microblog.py`，然后执行 `flask run`。这会启动一个 web 服务器，然后你可以在浏览器中输入`http://localhost:5000/`的URL 来访问。

在这一章，仍会继续在这个应用中开发，特别的，你将会学习到如何生成拥有复杂结构和许多动态组件的 web 页面。

本章的 Github 链接是：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.2), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.2.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.1...v0.2)

什么是模板?
===

我想要我的 `microblog` 应用的首页头部有一个欢迎用户的显示。当然现在应用中还没有用户的概念，在后面会加上。取而代之的是，我将会使用一个 `mock` 用户(模拟用户)，我用一个 Python 字典来实现：`user = {'username': 'Miguel'}`

创建一些模拟对象是一项比较有用的技术，这样使得你能专心于应用的一部分，而不用担心系统的其他部分还不存在。我想为我的应用设计一个首页，但是我不想被系统目前没有用户系统而烦恼，因此我模拟了一个用户对象，这样我就可以继续我的工作了。

视图函数返回了一个简单的字符串。我要做的就是将这个返回的字符串展开成一个完整的 HTML 页面。比如这样：

```python
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'miguel'}
    return '''
<html>
    <head>
        <title>Home Page - Microblog</title>
    </head>
    <body>
        <h1>Hello, ''' + user['username'] + '''!</h1>
    </body>
</html>'''
```

更新视图函数之后，重新启动应用，然后在浏览器中打开这个页面：

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch02-mock-user.png)

我希望你能同意我上述将 HTML 传递到浏览器的方式不是很好这个观点。当我想将用户的文章返回的时候，视图函数将会变得多么复杂，而且文章还会经常改变。而且应用还会有与其他 URL 绑定的视图函数，那么想象以下将来有一天我要改变应用的布局，那么我就得在每个视图函数中更新 HTML。所以这绝不是一个应对应用规模不断增长的方案。

如果你能将应用的逻辑和 web 页面的展示和布局分开的话，所有的东西都变得易于组织，不是吗？你甚至可以雇佣一个 web 页面设计者来创造非常牛逼的页面，而你只需要使用 Python 完成应用的逻辑代码。

模板帮助实现了表示层和业务逻辑的分离。在 Flask 中，模板被写在单独的文件中，存储在应用的包的 `templates` 文件夹中。因此确保你在 `microblog` 文件夹下，然后创建 `templates` 文件夹: `(venv) $ mkdir app/templates`

下面你可以看到你的第一个模板，和上面 `index()` 视图函数返回的 HTML 页面很相似，将这个文件保存在 `app/templates/index.html`

```html
<html>
    <head>
        <title>{{ title }} - Microblog</title>
    </head>
    <body>
        <h1>Hello, {{ user.username }}!</h1>
    </body>
</html>
```

这一个标准的，非常简单的 HTML 页面。里面值得注意的是，两个花括号括起来的用于动态内容的部分。这表示里面的内容是变量，而且之后再运行的时候才能生成。

现在页面的展示已经放到了 HTML 模板中，视图函数就被简化了：

```python
from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    return render_template('index.html', title='Home', user=user)
```

是不是看起来更好了。在应用中试试看看模板是怎么工作的。一旦你在浏览器中载入了这个页面，你可能想看看 HTML 源代码和以前有什么不一样。

将模板转换成完整的 HTML 页面的过程叫做`渲染(rendering)`。为了渲染模板，我必须从 Flask 中导入一个函数叫做 `render_template`，这个函数将模板名字和一个模板参数的变量列表作为参数，然后返回同样的模板，但是已经用变量将模板中的占位符给替换了。

`render_template()` 函数调用了 [Jinja2](http://jinja.pocoo.org/) 模板引擎，该引擎是和 Flask 绑定在一起的。Jinja2 将会使用通过 `render_template` 函数传递进来的参数来替代对应的 `{{...}}` 块。

条件语句
===

你已经看到了 Jinja2 在渲染的时候是如何将真实的值替换占位符的，但是这只是 Jinja2 众多强大功能之一。比如，模板同样支持以 `{%...%}` 块的方式的控制语句。`index.html` 的下一个版本就是增加一个条件语句。

```html
<html>
    <head>
        {% if title %}
        <title>{{ title }} - Microblog</title>
        {% else %}
        <title>Welcome to Microblog!</title>
        {% endif %}
    </head>
    <body>
        <h1>Hello, {{ user.username }}!</h1>
    </body>
</html>
```

现在模板变得更智能了。如果视图函数忘记传递 title 参数，模板会使用默认值来渲染而不是一个空的 title。你可以通过移除 title 参数来查看条件语句是如何工作的。

循环
===

登录的用户可能想看在首页的所有用户最近的文章列表。那么应该如何扩展应用来支持这个功能呢。

同样，我会创建一些模拟的用户对象和一些文章对象来展示。

```python
from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)
```

为了展示用户文章，我使用了个列表，里面每个元素都是一个字典，并且都包含 `author` 和 `body` 字段。当我要实现用户和文章的时候我也会尽量保留现在的字段名字，所以在之后我在设计和测试之中使用的这些对象依然有效。

在模板方面我必须得解决一个新的问题。posts 列表可能有任意多个元素，它取决于视图函数决定多少个 posts 将会在页面展示。模板不能对有多少 posts 做任何假定，因此它必须以通用的方式来渲染任意视图函数传递给它的 posts。

对于这个问题，Jinja2 提供了 `for` 控制结构：

```html
<html>
    <head>
        {% if title %}
        <title>{{ title }} - Microblog</title>
        {% else %}
        <title>Welcome to Microblog</title>
        {% endif %}
    </head>
    <body>
        <h1>Hi, {{ user.username }}!</h1>
        {% for post in posts %}
        <div><p>{{ post.author.username }} says: <b>{{ post.body }}</b></p></div>
        {% endfor %}
    </body>
</html>
```

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch02-mock-posts.png)

是不是很简单？

模板继承
===

大多数 web 应用在页面顶部都会有一个导航栏，上面放置一些比较常用的链接，比如编辑个人资料，登录登出等。我可以很容易的给 `index.html` 模板来添加一个导航栏，但是随着应用的规模增长我需要将同样的导航栏放到其他页面上。但是我不想在多个 HTML 模板中维护数个一样的导航栏。`not repeat yourself` 不要重复你自己！

Jinja2 拥有模板继承特性就是来解决这个问题的。在本质上，你要做的就是将所有模板共同的东西拿到一个基础模板中，然后其他模板从这个基础模板派生。

所以我要做的就是定义一个叫 `base.html` 的基础模板，其包含了一个简单的导航栏以及之前实现的简单逻辑。你需要将下面的代码保存到`app/template/base.html` 模板中

```html
<html>
    <head>
      {% if title %}
      <title>{{ title }} - Microblog</title>
      {% else %}
      <title>Welcome to Microblog</title>
      {% endif %}
    </head>
    <body>
        <div>Microblog: <a href="/index">Home</a></div>
        <hr>
        {% block content %}{% endblock %}
    </body>
</html>
```

在这个模板中我使用了 `block` 控制语句来定义派生模板可以插入的位置。block 的名字是唯一的，这样派生模板就可以在提供他们的内容时候引用。

在有了基础模板，我现在可以让 `index.html` 来继承 `base.html`

```html
{% extends "base.html" %}

{% block content %}
    <h1>Hi, {{ user.username }}!</h1>
    {% for post in posts %}
    <div><p>{{ post.author.username }} says: <b>{{ post.body }}</b></p></div>
    {% endfor %}
{% endblock %}
```

既然 `base.html` 现在可以承担通用的页面结构，我将这些元素从 `index.html` 中移除了，只留下了内容部分。`extends` 语句在两个模板间建立了继承关系，因此 Jinja2 知道当要渲染 `index.html` 的时候，需要将其嵌入到 `base.html`。两个模板会来用名字 `content` 来匹配 `block` 语句，这也是 Jinja2 为什么知道如何将两个模板合并成一个。现在如果我需要为应用创建其他页面的话，我可以从同样的 `base.html` 来派生模板，这也是我可以使得应用的所有页面都看起来相似但是又不会感觉到重复。

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch02-inheritance.png)
