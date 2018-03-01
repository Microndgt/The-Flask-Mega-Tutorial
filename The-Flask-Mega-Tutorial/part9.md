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

应用看起来比以前更好了，但是在首页展示所有文章很快就会成为问题。如果一个用户关注了上千其他用户怎么办？或者是上百万？你可以想象，管理这么多文章的列表将会非常低效。

为了解决这个问题，我将对文章列表进行分页。也就是我只会展示一部分文章，然后包含所有文章的浏览链接。Flask-SQLAlchemy 本身就支持分页，使用 `paginate()` 查询方法。比如，我想获取一个用户前二十的关注文章，我可以用 `paginate()` 替换 `all()` 来终止查询。

```shell
>>> user.followed_posts().paginate(1, 20, False).items
```

`paginate` 方法可以在任何 Flask-SQLAlchemy 的查询对象上调用。它需要三个参数：

- 页码，从 1 开始
- 每页的条目数
- 错误标志。如果是 `True`，当超过页数限制则会返回客户端一个 404 错误。如果是 `False` 将返回一个空列表。

`paginate` 方法返回的是 `Pagination` 对象。该对象的 `item` 属性包含了请求页的条目列表。`Pagination` 对象还有其他有用的东西，一会我们再讨论。

现在我们来考虑下如何在 `index()` 视图函数上实现分页。我可以通过在应用上添加一个配置项来决定每页显示多少文章开始：

```python
class Config(object):
    # ...
    POSTS_PER_PAGE = 3
```

在配置文件里配置这些应用级别的"旋钮"是一个很好的方式，这样我就可以在相同的地方来对这些配置进行修改。在最后的应用里，会使用比 3 大的数字来返回文章列表，现在作为测试就使用小一点的数字了。

下一步，我需要决定如何将 page 参数和应用的 URL 整合在一起。通用的方式是使用查询参数来指定一个可选的页码，如果没有给定默认是 1。下面是我将要实现的 URL 的几个例子：

- 页面 1：`http://localhost:5000/index`
- 页面 1：`http://localhost:5000/index?page=1`
- 页面 3：`http://localhost:5000/index?page=3`

为了能获取到查询字符串，我使用了 Flask 的 `request.args` 对象。你已经在第五章的时候看到了我在用户登录的时候用来获取 next 查询参数。

下面你可以看到我如何在首页和探索页视图函数上增加分页了：

```python
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # ...
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    return render_template("index.html", title='Explore', posts=posts.items)
```

这样，两个路由就可以决定展示哪一页，可以从 page 查询参数也可以是默认的 1，然后使用 `paginate()` 方法来获取到希望页码的文章列表。`POSTS_PER_PAGE` 配置项决定了每次返回文章列表的条目数，该配置可以从 `app.config` 对象中获取。

可以看到，这一切都很简单，而且每次做的代码改动都很少。我在完成应用的每一部分的时候都没有依赖其他部分怎么工作，这样使得我可以写出更模块化和更健壮的应用，使得应用更加容易扩展和测试，更不容易出错。

去尝试一下分页吧，不过首先需要 3 篇文章。在探索页更容易点，因为它会显示所有用户的文章。你将会看到最近的三篇文章，如果你想看下一个三篇，那么在浏览器中输入 `http://localhost:5000/explore?page=2`

分页导航
===

下一步就是在文章列表底部添加导航到上一页和下一页的链接。还记得 `paginate()` 调用返回的是 Flask-SQLAlchemy 的 `Pagination` 类的对象么？目前为止，我只使用了 `items` 属性，包含了所有查询出来的条目列表。但是这个对象还有其他一些很有用的属性用来构建分页链接：

- `has_next`: 如果为 True 表明当前页面之后还有至少一页
- `has_prev`: 如果为 True 表明当前页面之前还有至少一页
- `next_num`: 下一页的页码
- `prev_num`: 上一页的页码

有了这四个组件，我可以生成下一页和上一页的链接，然后将其传递到模板进行渲染。

```python
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # ...
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                            posts=posts.items, next_url=next_url,
                            prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                            next_url=next_url, prev_url=prev_url)
```

在这两个视图函数中的 `next_url` 和 `prev_url` 在还有页面的时候通过 `url_for` 返回一个 URL 对象。如果当前页是文章集合的某一个端点，那么`has_prev` 或者 `has_next` 属性将会是 False，那么对应方向的链接将会是 None。

一个 `url_for()` 函数比较有意思的地方是你可以给它添加关键字参数，如果该名字对应的参数没有直接加在 URL 上，那么 Flask 将会将它作为 URL 的查询参数。

分页链接将会在 `index.html` 模板上设置，现在就让我们在文章列表下面渲染它们吧：

```html
...
{% for post in posts %}
    {% include '_post.html' %}
{% endfor %}
{% if prev_url %}
<a href="{{ prev_url }}">Newer posts</a>
{% endif %}
{% if next_url %}
<a href="{{ next_url }}">Older posts</a>
{% endif %}
...
```

该链接将同时加在首页和探索页面。第一个链接起名为 `Newer posts`，它将会显示最新的文章。第二个链接起名为 `Older posts` 将会显示后面的文章。如果任意一个链接是 None，那么都不会被显示出来。

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch09-pagination.png)

用户信息页面的分页
===

现在首页是比较高效的。然后还有一个在用户信息页的文章列表，只显示该用户的所有文章。为了保持一致，用户信息页的文章列表也将采取分页的形式。

首先我对用户信息页视图函数进行修改，这依然是一个模拟文章对象列表。

```python
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
```

为了获取用户的所有文章列表，我使用了已经由 SQLAlchemy 设置的 `user.posts` 关系，该关系通过 `db.relationship()` 定义在 `User` 模型中。我使用了 `order_by()` 子句以获取最新的文章，然后进行分页。注意到通过 `url_for()` 产生的分页链接需要额外的 `username` 参数，所以它们依然会连接到用户信息页面。

最后，对 `user.html` 模板进行修改：

```html
...
{% for post in posts %}
    {% include '_post.html' %}
{% endfor %}
{% if prev_url %}
<a href="{{ prev_url }}">Newer posts</a>
{% endif %}
{% if next_url %}
<a href="{{ next_url }}">Older posts</a>
{% endif %}
```

在完成分页功能之后，你可以设置 `POSTS_PER_PAGE` 配置项一个更合理的值：

```python
class Config(object):
    # ...
    POSTS_PER_PAGE = 25
```
                    
