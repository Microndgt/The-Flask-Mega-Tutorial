The Flask Mega-Tutorial Part VI:: Profile Page and Avatars

原文地址： [The Flask Mega-Tutorial Part VI: Profile Page and Avatars](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vi-profile-page-and-avatars)

这是 Flask Mega-Ttorial 系列的第六部分，我将告诉你如何创建个人主页。

本章将致力于为应用添加个人主页。个人主页用来展示用户的相关信息，其个人信息由本人录入。 我将为你展示如何动态地生成每个用户的主页，并提供一个编辑页面给他们来更新个人信息。

本章的 GitHub 链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.6), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.6.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.5...v0.6).

个人主页
===

作为创建个人主页的第一步，让我们为其URL */user/<username>* 新建一个对应的视图函数。
```python
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)
```

我用来装饰该视图函数的`@app.route`装饰器看起来和之前的有点不一样。 本例中被`<`和`>`包裹的URL `<username>`是动态的。 当一个路由包含动态组件时，Flsk 将接受该部分 URL 中的任何文本，并将以实际文本作为参数调用该视图函数。 例如，如果客户端浏览器请求URL `/user/susan`，则视图函数将被调用，其参数 `username` 被设置为`'susan'`。 因为这个视图函数只能被已登录的用户访问，所以我添加了`@login_required`装饰器。

这个视图函数的实现相当简单。 我首先会尝试在数据库中以用户名来查询和加载用户。 之前你见过通过调用`all()`来得到所有的结果的查询，或是调用`first()`来得到结果中的第一个或者结果集为空时返回 `None` 的查询。 在本视图函数中，我使用了`first()`的变种方法，名为`first_or_404()`，当有结果时它的工作方式与`first()`完全相同，但是在没有结果的情况下会自动发送[404 error](https://en.wikipedia.org/wiki/HTTP_404)给客户端。 以这种方式执行查询，我省去检查用户是否返回的步骤，因为当用户名不存在于数据库中时，函数将不会返回，而是会引发 404 异常。

如果执行数据库查询没有触发 404 错误，那么这意味着找到了具有给定用户名的用户。 接下来，我为这个用户初始化一个虚拟的用户动态列表，最后用传入的用户对象和用户动态列表渲染一个新的*user.html*模板。

*user.html*模板如下所示：
```html
{% extends "base.html" %}

{% block content %}
    <h1>User: {{ user.username }}</h1>
    <hr>
    {% for post in posts %}
    <p>
    {{ post.author.username }} says: <b>{{ post.body }}</b>
    </p>
    {% endfor %}
{% endblock %}
```

个人主页虽然已经完成了，但是网站上却没有一个入口链接。我将会在顶部的导航栏中添加这个入口链接，以便用户可以轻松查看自己的个人资料：
```html
    <div>
      Microblog:
      <a href="{{ url_for('index') }}">Home</a>
      {% if current_user.is_anonymous %}
      <a href="{{ url_for('login') }}">Login</a>
      {% else %}
      <a href="{{ url_for('user', username=current_user.username) }}">Profile</a>
      <a href="{{ url_for('logout') }}">Logout</a>
      {% endif %}
    </div>
```

这里唯一有趣的变化是用来生成链接到个人主页的`url_for()`调用。 由于个人主页视图函数接受一个动态参数，所以`url_for()`函数接收一个值作为关键字参数。 由于这是一个指向当前登录个人主页的链接，我可以使用 Flask-Login的`current_user`对象来生成正确的URL。

![个人主页](http://upload-images.jianshu.io/upload_images/4961528-9083e29278d26e8c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

尝试点击顶部的 `Profile` 链接就能将你带到自己的个人主页。 此时，虽然没有链接来访问其他用户的主页，但是如果要访问这些页面，则可以在浏览器的地址栏中手动输入网址。 例如，如果你在应用中注册了名为“john”的用户，则可以通过在地址栏中键入*http:// localhost:5000/user/john*来查看该用户的个人主页。

头像
===

我相信你也觉得我刚刚建立的个人主页非常枯燥乏味。为了使它们更加有趣，我将添加用户头像。与其在服务器上处理大量的上传图片，我将使用[Gravatar](http://gravatar.com/)为所有用户提供图片服务。

Gravatar 服务使用起来非常简单。 要请求给定用户的图片，使用格式为*https://www.gravatar.com/avatar/<hash>*的 URL 即可，其中`<hash>`是用户的电子邮件地址的 MD5 哈希值。 在下面，你可以看到如何生成电子邮件为`john@example.com`的用户的 Gravatar URL：
```shell
>>> from hashlib import md5
>>> 'https://www.gravatar.com/avatar/' + md5(b'john@example.com').hexdigest()
'https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
```

如果你想看一个实际的例子，我自己的 Gravatar URL是*https://www.gravatar.com/avatar/729e26a2a2c7ff24a71958d4aa4e5f35*。Gravatar 返回的图片如下：

![Miguel 的头像](http://upload-images.jianshu.io/upload_images/4961528-38e05911255ecccf.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

默认情况下，返回的图像大小是 80x80 像素，但可以通过向 URL 的查询字符串添加 `s` 参数来请求不同大小的图片。 例如，要获得我自己 128x128 像素的头像，该 URL 是*https://www.gravatar.com/avatar/729e26a2a2c7ff24a71958d4aa4e5f35?s=128*。

另一个可传递给 Gravatar 的有趣参数是`d`，它让 Gravatar 为没有向服务注册头像的用户提供的随机头像。 我最喜欢的随机头像类型是“identicon”，它为每个邮箱都返回一个漂亮且不重复的几何设计图片。 如下：

![Identicon 头像](http://upload-images.jianshu.io/upload_images/4961528-d09629c52869c605.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

请注意，一些 Web 浏览器插件（如 Ghostery）会屏蔽 Gravatar 图像，因为它们认为 Automattic（Gravatar 服务的所有者）可以根据你发送的获取头像的请求来判断你正在访问的网站。 如果在浏览器中看不到头像，你在排查问题的时候可以考虑以下是否在浏览器中安装了此类插件。

由于头像与用户相关联，所以将生成头像 URL 的逻辑添加到用户模型是有道理的。
```python
from hashlib import md5
# ...

class User(UserMixin, db.Model):
    # ...
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
```

`User` 类新增的`avatar()`方法需要传入需求头像的像素大小，并返回用户头像图片的URL。 对于没有注册头像的用户，将生成“identicon”类的随机图片。 为了生成 MD5 哈希值，我首先将电子邮件转换为小写，因为这是 Gravatar 服务所要求的。 然后，因为 Python 中的 MD5 的参数类型需要是字节而不是字符串，所以在将字符串传递给该函数之前，需要将字符串编码为字节。

如果你对 Gravatar 服务很有兴趣，可以学习他们的[文档](https://gravatar.com/site/implement/images)。

下一步需要将头像图片插入到个人主页的模板中：
```html
{% extends "base.html" %}

{% block content %}
    <table>
        <tr valign="top">
            <td><img src="{{ user.avatar(128) }}"></td>
            <td><h1>User: {{ user.username }}</h1></td>
        </tr>
    </table>
    <hr>
    {% for post in posts %}
    <p>
    {{ post.author.username }} says: <b>{{ post.body }}</b>
    </p>
    {% endfor %}
{% endblock %}
```

使用 `User` 类来返回头像 URL 的好处是，如果有一天我不想继续使用 Gravatar 头像了，我可以重写`avatar()`方法来返回其他头像服务网站的URL，所有的模板将自动显示新的头像。

我的个人主页的顶部有一个不错的大头像，不止如此，底下的所有用户动态都会有一个小头像。 对于个人主页而言，所有的头像当然都是对应用户的。我将会在主页面上实现每个用户动态都用其作者的头像来装饰，这样一来看起来就非常棒了。

为了显示用户动态的头像，我只需要在模板中进行一个小小的更改：
```html
{% extends "base.html" %}

{% block content %}
    <table>
        <tr valign="top">
            <td><img src="{{ user.avatar(128) }}"></td>
            <td><h1>User: {{ user.username }}</h1></td>
        </tr>
    </table>
    <hr>
    {% for post in posts %}
    <table>
        <tr valign="top">
            <td><img src="{{ post.author.avatar(36) }}"></td>
            <td>{{ post.author.username }} says:<br>{{ post.body }}</td>
        </tr>
    </table>
    {% endfor %}
{% endblock %}
```

![头像](http://upload-images.jianshu.io/upload_images/4961528-a81330fb27bd9efd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

使用 Jinja2 子模板
===

我设计的个人主页，使用头像和文字组合的方式来展示了用户动态。 现在我想在主页也使用类似的风格来布局。 我可以复制/粘贴来处理用户动态渲染的模板部分，但这实际上并不理想，因为之后如果我想要对此布局进行更改，我将不得不记住要更新两个模板。

取而代之，我要创建一个只渲染一条用户动态的子模板，然后在*user.html*和*index.html*模板中引用它。 首先，我要创建这个只有一条用户动态 HTML 元素的子模板。 我将其命名为*app/templates/_post.html*， `_`前缀只是一个命名约定，可以帮助我识别哪些模板文件是子模板。
```html
    <table>
        <tr valign="top">
            <td><img src="{{ post.author.avatar(36) }}"></td>
            <td>{{ post.author.username }} says:<br>{{ post.body }}</td>
        </tr>
    </table>
```

我在*user.html*模板中使用了 Jinja2 的`include`语句来调用该子模板：
```html
{% extends "base.html" %}

{% block content %}
    <table>
        <tr valign="top">
            <td><img src="{{ user.avatar(128) }}"></td>
            <td><h1>User: {{ user.username }}</h1></td>
        </tr>
    </table>
    <hr>
    {% for post in posts %}
        {% include '_post.html' %}
    {% endfor %}
{% endblock %}
```

应用的主页还没有完善，所以现在我不打算在其中添加这个功能。

更多有趣的个人资料
===

新增的个人主页存在的一个问题是，真正显示的内容不够丰富。 用户喜欢在个人主页上展示他们的相关信息，所以我会让他们写一些自我介绍并在这里展示。 我也将跟踪每个用户最后一次访问该网站的时间，并显示在他们的个人主页上。

为了支持所有这些额外的信息，首先需要做的是用两个新的字段扩展数据库中的用户表：
```python
class User(UserMixin, db.Model):
    # ...
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
```

每次数据库被修改时，都需要生成数据库迁移。 在[第四章](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh/blob/master/docs/%E7%AC%AC%E5%9B%9B%E7%AB%A0%EF%BC%9A%E6%95%B0%E6%8D%AE%E5%BA%93.md)中，我向你展示了如何设置应用以通过迁移脚本跟踪数据库的变更。 现在有两个新的字段我想添加到数据库中，所以第一步是生成迁移脚本：
```shell
(venv) $ flask db migrate -m "new fields in user model"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added column 'user.about_me'
INFO  [alembic.autogenerate.compare] Detected added column 'user.last_seen'
  Generating /home/miguel/microblog/migrations/versions/37f06a334dbf_new_fields_in_user_model.py ... done
```

`migrate` 命令的输出表示一切正确运行，因为它显示 `User` 类中的两个新字段已被检测到。 现在我可以将此更改应用于数据库：
```shell
(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 780739b227a7 -> 37f06a334dbf, new fields in user model
```

我希望你认识到使用迁移框架是多么有用。 数据库中的用户数据仍然存在，迁移框架如同实施手术教学般地精准执行迁移脚本中的更改并且不损坏任何数据。

下一步，我将会把新增的两个字段增加到个人主页中：
```html
{% extends "base.html" %}

{% block content %}
    <table>
        <tr valign="top">
            <td><img src="{{ user.avatar(128) }}"></td>
            <td>
                <h1>User: {{ user.username }}</h1>
                {% if user.about_me %}<p>{{ user.about_me }}</p>{% endif %}
                {% if user.last_seen %}<p>Last seen on: {{ user.last_seen }}</p>{% endif %}
            </td>
        </tr>
    </table>
    ...
{% endblock %}
```

请注意，我用 Jinja2 的条件语句来封装了这两个字段，因为我只希望它们在设置后才可见。 目前，所有用户的这两个字段都是空的，所以如果现在运行应用，则不会看到这些字段。

记录用户的最后访问时间
===
让我们从更容易实现的`last_seen`字段开始。 我想要做的就是一旦某个用户向服务器发送请求，就将当前时间写入到这个字段。

为每个视图函数添加更新这个字段的逻辑，这么做非常的枯燥乏味。在视图函数处理请求之前执行一段简单的代码逻辑在 Web 应用中十分常见，因此 Flask 提供了一个内置功能来实现它。解决方案如下：
```python
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
```

Flsk 中的`@before_request`装饰器注册在视图函数之前执行的函数。这是非常有用的，因为现在我可以在一处地方编写代码，并让它在任何视图函数之前被执行。该代码简单地实现了检查`current_user`是否已经登录，并在已登录的情况下将`last_seen`字段设置为当前时间。我之前提到过，应用应该以一致的时间单位工作，标准做法是使用 UTC 时区，使用系统的本地时间不是一个好主意，因为如果那么的话，数据库中存储的时间取决于你的时区。最后一步是提交数据库会话，以便将上面所做的更改写入数据库。如果你想知道为什么在提交之前没有`db.session.add()`，考虑在引用`current_user`时，Flask-Login将调用用户加载函数，该函数将运行一个数据库查询并将目标用户添加到数据库会话中。所以你可以在这个函数中再次添加用户，但是这不是必须的，因为它已经在那里了。

如果在进行此更改后查看你的个人主页，则会看到“Last seen on”行，并且时间非常接近当前时间。 如果你离开个人主页，然后返回，你会看到时间在不断更新。

事实上，我在存储时间和在个人主页显示时间的时候，使用的都是 UTC 时区。 除此之外，显示的时间格式也可能不是你所预期的，因为实际上它是 Python dtime 对象的内部表示。 现在，我不会操心这两个问题，因为我将在后面的章节中讨论在 Web 应用中处理日期和时间的主题。

![最后访问时间](http://upload-images.jianshu.io/upload_images/4961528-959a36af22b86609.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

个人资料编辑器
===

我还需要给用户一个表单，让他们输入一些个人资料。 表单将允许用户更改他们的用户名，并且写一些个人介绍，以存储在新的`about_me`字段中。 让我们开始为它写一个表单类吧：
```python
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

# ...

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
```

我在这个表单中使用了一个新的字段类型和一个新的验证器。 对于“about_me”字段，我使用`TextAreaField`，这是一个多行输入文本框，用户可以在其中输入文本。 为了验证这个字段的长度，我使用了`Length`，它将确保输入的文本在 0 到140个字符之间，因为这是我为数据库中的相应字段分配的空间。

该表单的渲染模板代码如下：
```html
{% extends "base.html" %}

{% block content %}
    <h1>Edit Profile</h1>
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
            {{ form.about_me.label }}<br>
            {{ form.about_me(cols=50, rows=4) }}<br>
            {% for error in form.about_me.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
```

最后一步，使用视图函数将它们结合起来：
```python
from app.forms import EditProfileForm

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
```

这个视图函数处理表单的方式和其他的视图函数略有不同。如果`validate_on_submit()`返回`True`，我将表单中的数据复制到用户对象中，然后将对象写入数据库。但是当`validate_on_submit()`返回 `False` 时，可能是由于两个不同的原因。这可能是因为浏览器刚刚发送了一个 `GET` 请求，我需要通过提供表单模板的初始版本来响应。也可能是这种情况，浏览器发送带有表单数据的 `POST` 请求，但该数据中的某些内容无效。对于该表单，我需要区别对待这两种情况。当第一次请求表单时，我用存储在数据库中的数据预填充字段，所以我需要做与提交相反的事情，那就是将存储在用户字段中的数据移动到表单中，这将确保这些表单字段具有用户的当前数据。但在验证错误的情况下，我不想写任何表单字段，因为它们已经由 WTForms 填充了。为了区分这两种情况，我需要检查`request.method`，如果它是`GET`，这是初始请求的情况，如果是 `POST` 则是提交表单验证失败的情况。

![个人资料编辑器](http://upload-images.jianshu.io/upload_images/4961528-330719a5697b030a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

我将个人资料编辑页面的链接添加到个人主页，以便用户使用：
```
                {% if user == current_user %}
                <p><a href="{{ url_for('edit_profile') }}">Edit your profile</a></p>
                {% endif %}
```

请注意我巧妙使用的条件，它确保在查看自己的个人主页时出现编辑个人资料的链接，而在查看其他人的个人主页时不会出现。

![个人主页和编辑链接](http://upload-images.jianshu.io/upload_images/4961528-24fae0cd3c674e9f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

