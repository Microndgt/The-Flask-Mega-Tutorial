The Flask Mega-Tutorial Part VI: Profile Page and Avatars
===

原文地址: [The Flask Mega-Tutorial Part VI: Profile Page and Avatars](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vi-profile-page-and-avatars)

要创建用户个人资料页面，我们首先编写一个映射到/ user / <用户名> URL的新视图函数。

```
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
我用来声明这个视图函数的@app.route装饰器看起来有点不同于以前的。 

在这种情况下，我有一个动态组件，它被 <> 所包围的 username 组件所表示。 

当一个路由有一个动态组件时，Flask将匹配该部分URL中的任何文本，并将以实际文本作为参数调用视图函数。 

例如，如果客户端浏览器请求URL /user/susan ，则会将参数username设置为'susan'来调用view函数。 

这个视图函数只能被登录用户访问，所以我从Flask-Login中添加了@login_required装饰器。

这个视图函数的实现相当简单。 我首先尝试使用用户名查询从数据库加载用户。 

你之前已经看到，可以通过调用all()如果要获取所有结果all()来执行数据库查询。

如果你想只获取first()结果，则first()如果None result，则执行None 。 

在这个视图函数中，我使用了first()一个变体first_or_404() ，当有结果的时候，它的工作方式和first()完全一样，

但是在没有结果的情况下会自动向客户端发送404错误 。 

以这种方式执行查询，我省去检查查询是否返回用户，因为当用户名不存在于数据库中时，函数将不会返回，而是会引发404异常。

如果数据库查询不会触发404错误，那么这意味着找到了具有给定用户名的用户。 

接下来，我为这个用户初始化一个虚构的帖子列表，最后呈现一个新的user.html模板，我将该用户对象和帖子列表传递给它。

user.html模板如下所示：

```
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

个人资料页面现在已经完成，但是网站上的任何地方都不存在指向它的链接。 

为了让用户更容易检查自己的个人资料，我将在顶部的导航栏中添加一个链接

```
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

这里唯一有趣的变化是用于生成到配置文件页面链接的`url_for()`调用。 

由于用户配置文件视图函数采用动态参数，因此`url_for()`函数会将其作为关键字参数接收。 

由于这是一个链接，指向登录的用户配置文件，我可以使用Flask-Login的`current_user`生成正确的URL。

![用户资料页面](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch06-user-profile.png)


现在给应用程序一个尝试。 点击顶部的Profile链接应该带你到自己的用户页面。 

此时，其他用户的配置文件页面上将没有链接，但是如果要访问这些页面，则可以在浏览器的地址栏中手动输入网址。 

例如，如果你的应用程序中注册了名为“john”的用户，则可以通过在地址栏中键入*http://localhost:5000/user/john*来查看相应的用户配置文件。

**头像**

刚刚建立的用户首页可能比较简单，为了使它们更加漂亮，我将使用Gravatar服务为所有用户提供图片。

Gravatar服务使用起来非常简单。 要为特定用户请求图片，使用格式为https://www.gravatar.com/avatar/ <hash>的网址，

其中<hash>是用户电子邮件地址的MD5哈希值。 你可以在下面看到如何通过电子邮件john@example.com获取用户的Gravatar URL：

```
>>> from hashlib import md5
>>> 'https://www.gravatar.com/avatar/' + md5(b'john@example.com').hexdigest()
'https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
```

如果你想看到一个实际的例子，我自己的Gravatar URL是https://www.gravatar.com/avatar/729e26a2a2c7ff24a71958d4aa4e5f35 。

这是Gravatar为这个URL返回的内容：

![Gravatar](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch06-gravatar.jpg)

默认情况下，返回的图像大小是80x80像素，但可以通过向URL的查询字符串添加s参数来请求不同的大小。 

例如，要获得我自己的头像作为一个128x128像素的图像，URL是

*https://www.gravatar.com/avatar/729e26a2a2c7ff24a71958d4aa4e5f35?s=128 *

可以作为查询字符串参数传递给Gravatar的另一个有趣的参数是d ，它决定了Gravatar为没有向服务注册的头像的用户提供的图像。 我最喜欢的是“identicon”，它返回一个很好的几何设计，每个电子邮件都是不同的。 例如：

![identicon Gravatar](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch06-gravatar-identicon.png)

请注意，一些Web浏览器扩展（如Ghostery）会屏蔽Gravatar图像， 如果你在浏览器中看不到头像，请考虑问题可能是由于你在浏览器中安装了扩展程序。

由于头像与用户相关联，因此将生成头像网址的逻辑添加到用户模型是有意义的。

```
from hashlib import md5
# ...

class User(UserMixin, db.Model):
    # ...
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
```

User类的新avatar()方法返回用户头像图像的URL，按照像素大小缩放到所请求的大小。

对于没有注册头像的用户，将生成大众统一的图片。 为了生成MD5散列，我首先将电子邮件转换为小写，因为这是Gravatar服务所要求的。

然后，将邮件地址转为UTF-8，以及计算MD5

如果你有兴趣了解Gravatar服务提供的其他选项，请访问其文档网站 。

下一步是将头像图片插入到用户个人资料模板中：

```
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

让User类负责返回头像网址的好处是，如果有一天我决定Gravatar头像不是我想要的，我可以重写avatar()方法返回不同的网址，所有的模板将开始显示新的头像自动。

我在用户个人资料页面的顶部有一个大头像，下面是用户的帖子，每个帖子都有一个小头像。

为了显示个人帖子的头像，我只需要在模板中进行一个小的更改：

```
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

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch06-avatars.png)

**使用Jinja2子模板**

我设计了用户个人资料页面，以便显示用户写的帖子以及他们的头像。 

现在我想索引页面也显示具有类似布局的帖子。 我可以复制/粘贴处理文章渲染的模板部分，但是这实际上并不理想，

因为稍后如果我决定对此布局进行更改，我将不得不记住要更新这两个模板。

相反，我要创建一个只显示一个帖子的子模板，然后从user.html和index.html模板中引用它。

首先，我可以创建子模板，只有一个帖子的HTML标记。 我要命名这个模板app / templates / _post.html 。

`_`前缀只是一个命名约定，可以帮助我识别哪些模板文件是子模板。

```
    <table>
        <tr valign="top">
            <td><img src="{{ post.author.avatar(36) }}"></td>
            <td>{{ post.author.username }} says:<br>{{ post.body }}</td>
        </tr>
    </table>
```
要从user.html模板调用这个子模板，我使用Jinja2的include语句：

```
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
应用程序的索引页并不是特别丰富，我暂时不打算在那里添加这个功能。

**更丰富的配置文件**

新用户个人资料页面存在的一个问题是，他们没有显示太多内容。 用户喜欢在这些页面上讲一些关于他们的内容，所以我会让他们写一些关于他们自己的东西在这里展示。 我也将跟踪每个用户最后一次访问该网站的时间，并显示在他们的个人资料页面上。

为了支持所有这些额外的信息，首先需要做的是用两个新的字段扩展数据库中的users表：

```
class User(UserMixin, db.Model):
    # ...
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
```

每次数据库被修改时，都需要生成数据库迁移。 在第4章中，我向你介绍了如何设置应用程序以通过迁移脚本跟踪数据库更改。 现在我有两个新的字段，我想添加到数据库中，所以第一步是生成迁移脚本：

```
(venv) $ flask db migrate -m "new fields in user model"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added column 'user.about_me'
INFO  [alembic.autogenerate.compare] Detected added column 'user.last_seen'
  Generating /home/miguel/microblog/migrations/versions/37f06a334dbf_new_fields_in_user_model.py ... done
```

migrate命令的输出看起来不错，因为它显示User类中的两个新字段已被检测到。 现在我可以将此更改应用于数据库：

```
(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 780739b227a7 -> 37f06a334dbf, new fields in user model
```

我希望你认识到使用迁移框架是非常有用的。 数据库中的用户仍然存在，迁移框架通过迁移脚本中可以更改数据库结构而且不损坏任何数据。

下一步，我要将这两个新字段添加到用户配置文件模板中：

```
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

请注意，我在Jinja2的条件中包装这两个字段，因为我只希望它们在设置时可见。 在这一点上，这两个新字段对于所有用户都是空的，所以如果现在运行应用程序，则不会看到这些字段。

**记录用户的上次访问时间**

让我们从last_seen字段开始，这是两者中较容易的字段。 我想要做的就是写一个给定用户的这个字段的当前时间，只要这个用户发送一个请求到服务器。

添加登录来设置这个字段在每一个可以从浏览器请求的视图函数上显然是不切实际的，但是在请求被分派到视图函数之前执行一些通用逻辑是Web应用程序中的一个常见任务，Flask提供它作为本机功能。 看看解决方案：

```
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
```

Flask的`@before_request`装饰器注册装饰函数，在视图函数之前执行。

这是非常有用的，因为现在我可以在应用程序中的任何视图函数之前插入想要执行的代码，并且可以将它放在一个地方。

首先检查current_user是否已经登录，如果是，将last_seen字段设置为当前时间。

我之前提到过，服务器应用程序需要以一致的时间单位工作，标准做法是使用UTC时区。

使用系统的本地时间不是一个好主意，因为那么数据库中的内容取决于你的位置。 最后一步是提交数据库会话，以便将上面所做的更改写入数据库。

如果你想知道为什么在提交之前没有db.session.add() ，那么考虑到当你引用current_user ，Flask-Login将调用用户加载器回调函数，该函数将运行数据库查询，将目标用户置于数据库会话。 所以你可以在这个函数中再次添加用户，但是这不是必须的，因为它已经在那里了。

如果你在进行此更改后查看你的配置文件页面，则会看到`last_seen `一行，并且时间非常接近当前时间。 如果你离开个人资料页面，然后返回，你会看到时间不断更新。

我将这些时间戳存储在UTC时区的事实使得在配置文件页面上显示的时间也是UTC。

除此之外，时间的格式不是你所期望的，因为它实际上是Python datetime对象的内部表示。

现在，不用担心这两个问题，因为我将在后面的章节中讨论在Web应用程序中处理日期和时间的主题。

![头像](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch06-avatars.png)


**资料编辑器**

我还需要给用户一个表单，让他们输入一些关于自己的信息。 表单将允许用户更改他们的用户名，并且写一些关于他们自己的信息，以存储在新的about_me字段中。 我们开始为它写一个表单类：

```
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

# ...

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
```

我在这个表单中使用了一个新的字段类型和一个新的验证器。 对于“关于”字段，我使用的TextAreaField是一个多行框，用户可以在其中输入文本。 为了验证这个字段，我使用了Length ，它将确保输入的文本在0到140个字符之间，这是我为数据库中的相应字段分配的空间。

呈现此表单的模板如下所示：

```
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

最后，这里是将所有东西结合在一起的视图函数：

```
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

这个视图函数与处理表单的其他视图函数略有不同。 如果validate_on_submit()返回True我将表单中的数据复制到用户对象中，然后将对象写入数据库。

但是，当validate_on_submit()返回False ，可能因为是由于两个不同的原因。 第一，这可能是因为浏览器刚刚发送了一个GET请求，我需要通过提供表单模板的初始版本来做出响应。

当浏览器发送带有表单数据的POST请求时，也可能会出现这种情况，但该数据中的某些内容无效。

对于这种形式，我需要分别处理这两种情况。

当第一次请求GET请求时，我会用数据库中存储的数据先填充表单的字段，并且将用户重定向到资料修改页面

但在验证错误的情况下，我不会填充任何表单字段，因为那些已经由WTForms填充。

为了区分这两种情况，我检查了request.method ，它将是初始请求的GET ，而POST是验证失败的提交。

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch06-edit-profile.png)

为了方便用户访问个人资料编辑器页面，我可以在他们的个人资料页面添加一个链接：

```
                {% if user == current_user %}
                <p><a href="{{ url_for('edit_profile') }}">Edit your profile</a></p>
                {% endif %}
```

请注意我正在使用的判断条件，以确保在查看自己的配置文件时显示编辑链接，而在查看其他人的配置文件时不会显示编辑链接。

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch06-user-profile-link.png)