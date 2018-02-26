The Flask Mega-Tutorial Part IX: Pagination
===

原文地址: [The Flask Mega-Tutorial Part IX: Pagination](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ix-pagination)

这是 Flask Mega-Tutorial 第九部分，在本章我将会演示如何将数据库记录列表分页。

在第 8 章我已经支持目前社交网络上很流行的关注功能。在本章我将使得应用可以接受用户的文章，然后将它们显示在首页和个人页面上。

本章的 Github 链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.9), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.9.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.8...v0.9)

提交文章
===

首先从简单入手。首页需要一个用户可以输入新文章的表单。首先我创建一个表单类：

```python
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
```

下一步，我就可以为应用首页的模板上添加这个表单了。

```html
{% extends "base.html" %}

{% block content %}
    <h1>Hi, {{ current_user.username }}!</h1>
    <form action="" method="post">
        {{ form.hidden_tag() }}
        <p>
            {{ form.post.label }}<br>
            {{ form.post(cols=32, rows=4) }}<br>
            {% for error in form.post.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>{{ form.submit() }}</p>
    </form>
    {% for post in posts %}
    <p>
    {{ post.author.username }} says: <b>{{ post.body }}</b>
    </p>
    {% endfor %}
{% endblock %}
```

该表单处理和以前的表单处理差不多。最后的部分是在视图函数上创建和处理表单。

```python
from app.forms import PostForm
from app.models import Post

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
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
    return render_template("index.html", title='Home Page', form=form,
```

让我们逐一的查看这个视图函数

- 首先导入了 `Post` 和 `PostForm` 类
- 两个路由上我都支持 POST 请求，并且绑定到 `index` 试图函数，另外还支持 `GET` 请求。现在这个视图函数就支持接收表单数据了。
- 表单处理逻辑就是将新的 `Post` 记录插入到数据库中。
- 模板接收 `form` 对象，这样它就可以渲染文本区域。

在我继续之前，我想讨论一下关于 web 表单处理相关比较重要的东西。注意我在处理表单数据之后是怎么做的，我通过将请求重定向到首页来结束请求。我可以容易的跳过重定向并且允许试图函数继续到模板渲染部分，因为这已经是首页视图函数了。

那么，为什么重定向呢？使用重定向是为提交 web 表单的 `POST` 请求生成响应的标准方式。这帮助减轻浏览器关于如何实现刷新命令的烦恼。所有浏览器当你点击刷新的时候都会重新发起上一个请求。如果一个表单提交的 `POST` 请求返回普通的响应，那么刷新会导致重新提交这个表单。但这是不期望发生的，浏览器会询问用户是否重复提交，但是大多数用户并不能明白为什么浏览器询问他。如果 `POST` 请求被重定向应答，那么浏览器就会在刷新的时候发送 `GET` 请求。现在最后一个请求不再是 POST 请求了，现在刷新操作就以可以预知的方式工作了。

最简单的技巧叫做 [Post/Redirect/Get](https://en.wikipedia.org/wiki/Post/Redirect/Get) 模式。它阻止了用户在提交表单后在无意间刷新页面导致插入重复的文章。

显示文章
===

如果你回忆下，我在首页展示文章的地方创建了几篇模拟文章。这些文章是在 index 视图函数上以 Python 列表显式建立的。

```python
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
```

但是现在 User 模型有了 `followed_posts()` 方法，它会查询并且返回一个给定用户所有想看到的文章。现在我就可以用真实的文章来替换模拟文章。

```python
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # ...
    posts = current_user.followed_posts().all()
    return render_template("index.html", title='Home Page', form=form,
                           posts=posts)
```

User 类的 `followed_posts` 方法返回一个 SQLAlchemy 查询对象用于从数据库提取用户感兴趣的文章。在这个查询对象上调用 `all()` 会触发查询的执行，并且返回一个所有结果的列表，正如上面的模拟文章列表，因此模版也不需要改变。

让查找用户并且关注更容易
===

你也许已经注意到，目前在应用中查找一个用户并且关注不是很容易。事实上，根本没有可以看到其他用户的方式。现在我将会加上这一功能。

我将要创建一个叫做 Explore 的新页面，这个页面就像首页一样的工作，但不是只显示关注用户的文章，它会显示所有用户的全局文章流。下面是新的 explore 视图函数。

```python
@app.route('/explore')
@login_required
def explore():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Explore', posts=posts)
```

你注意到了吗？`render_template()`调用使用了 `index.html` 模版，这是我在应用首页中使用的模版。因为探索页和首页非常相似，因此我决定使用这个模版。但是和首页不同的是，我不想包含可以写文章的表单，因此在这个视图函数中我在调用 `render_template()` 方法的时候没有包含 form 参数。

为了阻止 `index.html` 渲染不存在的 web 表单，我添加了一个条件，这样只在 form 存在的时候渲染。

```html
{% extends "base.html" %}

{% block content %}
    <h1>Hi, {{ current_user.username }}!</h1>
    {% if form %}
    <form action="" method="post">
        ...
    </form>
    {% endif %}
    ...
{% endblock %}
```

我也将会在导航栏上添加一个到探索页的链接：

```html
<a href="{{ url_for('explore') }}">Explore</a>
```

还记得在 `_post.html` 子模板会在用户信息页面中渲染用户文章。这是一段短小的模板，但是通用，所以被单独分离出来这样就可以被其他模板使用。现在我对其做一些小的改进，将文章的作者用户名显示为一个链接。

```html
<table>
    <tr valign="top">
        <td><img src="{{ post.author.avatar(36) }}"></td>
        <td>
            <a href="{{ url_for('user', username=post.author.username) }}">
                {{ post.author.username }}
            </a>
            says:<br>{{ post.body }}
        </td>
    </tr>
</table>
```

现在我可以用这个子模板来在首页和探索页渲染博客文章了：

```html
...
{% for post in posts %}
    {% include '_post.html' %}
{% endfor %}
...
```

子模板需要一个叫 post 的变量存在，这也是在首页模板中循环变量的名字，因此可以正常工作。

通过这些小的改变，应用的可用性得到了大的提高。现在一个用户可以访问探索页来阅读不认识用户的文章。通过这些文章，只需要轻轻在用户名上一点，可以找到作者并且去关注他。

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch09-explore.png)

文章分页
===

