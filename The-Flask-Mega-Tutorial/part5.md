The Flask Mega-Tutorial Part V: User Logins
===

原文地址: [The Flask Mega-Tutorial Part V: User Logins](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins)

这是 Flask Mega-Tutorial 系列的第五节，在这里我将会向你介绍如何创建一个用户登录子系统。

在第三章你学习了如何创建一个用户登录表单，在第四章你学习到了如何使用数据库。在这章你将会学到如何将前两章学习到的东西组合起来以创建一个简单的用户登录系统。

本章的 Github 链接是：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.5), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.5.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.4...v0.5)

密码哈希
===

在第四章中，在用户模型里创建了一个 `password_hash` 字段，但是到目前为止没有使用。这个字段是为了存储用户密码的哈希，将来会用来验证用户在登录中输入的密码。密码哈希是一个比较复杂的问题，但是有许多易用的库实现了在应用中非常简单的调用它们的逻辑。

一个实现了密码哈希的库是 [Werkzeug](http://werkzeug.pocoo.org/)，可能你在安装 Flask 的时候看到了这个 Flask 核心依赖之一的库。因为它是一个依赖库，因此在你当前的虚拟环境中，Werkzeug 已经安装了。下面的 Python shell 会话向你展示了如何哈希一个密码：

```shell
>>> from werkzeug.security import generate_password_hash
>>> hash = generate_password_hash('foobar')
>>> hash
'pbkdf2:sha256:50000$vT9fkZM8$04dfa35c6476acf7e788a1b5b3c35e217c78dc04539d295f011f01f18cd2175f'
```

在这个例子中，密码 `foobar` 通过一系列的加密操作被转换成了一个长的编码后的字符串，而且这些加密操作目前是没有反向操作的，意味着即使你得到了这个哈希值，你也没法从哈希值推出原始密码。而且如果你哈希同样的密码多次，你将会得到不同的结果，这样就可以确保不可能通过比较两个密码的哈希值一样来判断两个用户的密码也一样这种情况。

通过 Werkzeug 的第二个函数可以完成验证操作：

```shell
>>> from werkzeug.security import check_password_hash
>>> check_password_hash(hash, 'foobar')
True
>>> check_password_hash(hash, 'barfoo')
False
```

验证函数使用刚才生成的密码哈希和用户登录时候键入的密码作为参数。如果密码匹配哈希的话，该函数返回 True，否则返回 False

整个的密码哈希逻辑可以被实现为在用户模型中的两个新方法：

```python
from werkzeug.security import generate_password_hash, check_password_hash

# ...

class User(db.Model):
    # ...

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

有了这两个方法，用户对象可以支持安全的密码验证，而且也不需要存储原始密码。下面是如何使用这些新方法：

```shell
>>> u = User(username='susan', email='susan@example.com')
>>> u.set_password('mypassword')
>>> u.check_password('anotherpassword')
False
>>> u.check_password('mypassword')
True
```

Flask-Login 入门
===

在本章我将给你介绍一个非常流行的 Flask 扩展叫做 [Flask-Login](https://flask-login.readthedocs.io/)。这个扩展管理了用户登录状态，因此用户就可以登录到应用，应用会记住用户登录的状态，所以用户就可以访问其他页面。它还提供了 `remember me` 功能 —— 即使在用户关闭浏览器也能保持用户登录状态。下面是 Flask-Login 的安装：

```shell
(venv) $ pip install flask-login
```

和其他扩展类似，Flask-Login 需要在 `app/__init__.py` 中应用实例之后创建并且初始化。下面是这个扩展是如何初始化的:

```python
# ...
from flask_login import LoginManager

app = Flask(__name__)
# ...
login = LoginManager(app)

# ...
```

改进用户模型
===

Flask-Login 扩展需要配合应用的用户模型一起工作，并且期望特定的属性和方法在用户模型中被实现。这样做很方便，因为只要这些需要的项被加入到模型中，Flask-Login 就不需要其他的依赖了。所以它可以和基于任何数据库系统的用户模型一起工作。

四个必须项罗列如下：

1. `is_authenticated`: 如果用户拥有有效验证的话为 True 否则为 False
2. `is_active`: 如果用户账户是活跃的则为 True, 否则为 False
3. `is_anonymous`: 对于正常用户是 False，特殊的匿名用户是 True
4. `get_id()`: 返回用户的唯一标识符字符串(Python2 中是 Unicode)

当然我可以很容易的实现这四个属性，但是鉴于它们很常用，Flask-Login 提供了一个 `mixin` (混入) 类叫做 `UserMixin`，这个类中包含了适配大部分用户模型类的一般实现。下面是这个混入类如何加入到模型中：

```python
# ...
from flask_login import UserMixin

class User(UserMixin, db.Model):
    # ...
```

用户载入函数
===

Flask-Login 通过在 Flask 的用户 session 中存储用户的唯一标识符来跟踪登录用户，这个 session 是为每一个登录应用的用户开辟的存储区域。每一次登录用户浏览新的页面，Flask-Loing 会从 session 中取得用户ID，然后将用户载入到内存。

因为 Flask-Login 和数据库无关，因此需要应用来协助载入一个用户。因此，扩展期望应用来实现一个用户载入的函数，这样就可以根据给定的用户 ID 来载入一个用户。这个函数一般会放到 `app/models.py` 中：

```python
from app import login
# ...

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
```

用户载入器通过 `@login.user_loader` 装饰器注册到 Flask-Login。`id` 是 Flask-Login 作为字符串参数传递到函数中的，因此需要将字符串转换成数字类型用来查询。

登录用户
===

让我们重新回顾一下登录视图函数，目前只实现了一个模拟的登录然后弹出一个 `flash()` 消息。现在应用已经可以连接用户数据库并且知道如何去验证密码，那么登录视图函数就可以完成了。

```python
# ...
from flask_login import current_user, login_user
from app.models import User

# ...

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
```

前两行处理了一种特殊情况，就是你已经登录了，但是你又去访问了 `/login` URL去登录。明显这是一个错误，因此我需要阻止它。Flask-Login 的 `current_user` 变量可以在获取代表客户端请求的用户对象的处理中随时使用。这个变量的值可能是从数据库来的用户对象(Flask-Login 从上面我们定义的用户载入函数中获取用户对象)，或者当用户没有登录的时候是一个特殊的匿名用户对象。还记得 Flask-Login 在用户对象中需要的那几个属性吗？其中一个就是 `is_authenticated`，用来方便的检查用户是否登录。如果用户已经登录，我只需要将他们重定向到首页。

在 `flash()` 调用的前面，我现在可以真实的登录用户了。第一步是从数据库中载入用户。form 表单提交会包含用户名信息，因此我可以使用用户名来查询数据库以找到相应的用户。为了查询用户我使用了 `filter_by()` 这个 SQLAlchemy 查询对象。`filter_by()` 函数的结果只会包含匹配用户名的对象。因为我知道肯定要么只有一条，要么没有，所以我通过调用 `first()` 来完成查询，这个方法如果用户存在则返回一个用户对象，如果不存在则返回 None。在第四章你已经看到如果在查询中使用 `all()` 方法，查询执行后你会得到匹配这个查询的结果列表。`first()` 方法是另外一个经常使用的查询来获取单条结果。

如果我得到了关于用户名的匹配，那么接下来我会检查表单提供的密码和查询出来的用户对象的密码是否匹配。这个过程会通过上面我定义的 `check_password()` 方法完成。首先会从用户对象中拿出密码哈希，然后检查用户输入的密码是否匹配这个密码哈希。因此我现在会有两种错误可能：用户名可能无效，或者密码不正确。不论哪种情况，我都会闪现一条消息，并且重定向页面到登录，这样用户可以重试。

如果用户名和密码都正确，之后我会调用 Flask-Login 中的 `login_user()` 函数。这个函数会将用户注册为登录状态，这意味着将来用户访问的任何页面都会将 `current_user` 变量置为这个用户。

为了完成登录过程，我只是将新登录的用户重定向到了首页。

登出用户
===

我需要将用户登出。这可以通过 Flask-Login 的 `logout_user()` 函数完成，下面是一个登出的视图函数：

```python
# ...
from flask_login import logout_user

# ...

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
```

为了向用户暴露这个接口，我可以将导航栏上的登录链接在用户登录之后自动的切换到登出链接。这可以通过在 `base.html` 模板中添加一个条件判断完成：

```html
 <div>
    Microblog:
    <a href="{{ url_for('index') }}">Home</a>
    {% if current_user.is_anonymous %}
    <a href="{{ url_for('login') }}">Login</a>
    {% else %}
    <a href="{{ url_for('logout') }}">Logout</a>
    {% endif %}
</div>
```

`is_anonymous` 属性是 Flask-Login 通过 `UserMixin` 类添加到用户对象的属性之一。`current_user.is_anonymous` 表达式在用户没有登录的情况下是 True。

需要用户登录
===

Flask-Login 提供了一个非常有用的特性：在浏览应用特定页面之前必须登录。如果有用户在没有登录的状态下试图浏览受保护的页面，那么 Flask-Login 会自动的将用户重定向到登录页面，只有当登录成功之后才会将用户导向至登录之前想访问的页面。

为了实现这一特性，Flask-Login 需要知道处理登录的视图函数是什么，这个可以添加到 `app/__init__.py`

```python
# ...
login = LoginManager(app)
login.login_view = 'login'
```

上面的 `'login'` 值是登录视图的函数名字。也就是说，你可以使用 `url_for()` 获取到相应的 URL。

Flask-Login 是通过一个 `@login_required` 装饰器来阻止匿名用户来访问受保护的视图函数的。当你在视图函数的 `@app.route` 装饰器下面加上这个装饰器，那么这个函数就变成受保护的，也会拒绝没有权限的用户访问。下面就是如何给应用的首页视图函数添加这个装饰器：

```python
from flask_login import login_required

@app.route('/')
@app.route('/index')
@login_required
def index():
    # ...
```

剩下的就是如何在成功登陆之后跳转到用户想要访问的页面。当用户在没有登录的情况下访问受 `@login_required` 保护的视图函数就会被跳转到登录页面，但是需要在这个跳转中加入一些信息，这样才可以在登录之后跳转回去。如果用户访问 `/index`，那么 `@login_required` 就会拦截这个请求并且跳转到 `/login`，并且会在 URL 中加入一个查询字符串，组成了一个完成的跳转 URL: `/login?next=/index`。next 查询字符串会设置为原始的 URL，这样在登录之后应用就可以跳转回去了。

下面是展示了如何读取和处理 `next` 查询字符串的一段代码：

```python
from flask import request
from werkzeug.urls import url_parse

@app.route('/login', methods=['GET', 'POST'])
def login():
    # ...
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    # ...
```

在通过调用 Flask-Login 的 `login_user()` 函数登录用户之后，next 查询字符串的值就会被获取。Flask 提供了一个包含了客户端发送过来所有信息的 request 变量。特别的，`request.args` 属性以字典的方式暴露了所有查询字符串的内容。关于是否在成功登陆后跳转有以下三个需要考虑的地方：

1. 如果登录 URL 没有一个 next 参数，那么用户就会被跳转到首页
2. 如果登录 URL 的 next 参数被设置成了相对路径，那么用户就会被跳转到那个 URL
3. 如果登录 URL 的 next 参数被设置成了包含域名的完整路径，则用户会被跳转到首页

第一，二种情况比较好理解。第三种其实是使得应用变得更安全。攻击者可能在 next 参数中插入一段跳转到恶意站点的 URL，因此应用只能跳转那些是相对路径的，确保了跳转之后还是在本站点中。为了判断 URL 是否是相对或者绝对的，我使用了 Werkzeug 的 `url_parse()` 函数来解析参数并且检查 `netloc` 组件是否设置。

`[译者注]`：一个 URL 的组成以实例解释如下：

```
# URL: http://www.baidu.com/index.php?username=github
scheme='http', netloc='www.baidu.com', path='/index.php', params='', query='username=github', fragment=''
```

在模板中展示登录用户
===

目前系统已经有真实用户了，所以现在可以将以前的模拟用户删除了，使用真正的用户。我现在在模板中使用 Flask-Login 的 `current-user`：

```html
{% extends "base.html" %}

{% block content %}
    <h1>Hi, {{ current_user.username }}!</h1>
    {% for post in posts %}
    <div><p>{{ post.author.username }} says: <b>{{ post.body }}</b></p></div>
    {% endfor %}
{% endblock %}
```

而且我可以在视图函数中移除向模板中传递的 `user` 参数

```python
@app.route('/')
@app.route('/index')
def index():
    # ...
    return render_template("index.html", title='Home Page', posts=posts)
```

下来可以测试登录和登出功能是否正常。因为还没有加入用户注册功能，因此唯一的添加用户的方法就是用 Python shell 来操作数据库。因此我运行了 `flask shell` 并且输入以下的命令来注册一个用户：

```shell
>>> u = User(username='susan', email='susan@example.com')
>>> u.set_password('cat')
>>> db.session.add(u)
>>> db.session.commit()
```

如果你启动应用然后访问 `http://localhost:5000/` 或者 `http://localhost:5000/index`，你就会被重定向到登录页面，在你登录之后，你就会被跳转到原始页面，那里就会看到个人问候语。

用户注册
===

在这章中最后一个要构建的就是用户注册功能，这样用户就可以通过一个 web 表单来注册新用户。让我们从在 `app/forms.py` 中创建 web 表单类开始吧：

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

# ...

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
```

这个新表单会关联到几个验证函数。首先 `email` 字段在 `DataRequired()` 验证之后还添加了一个新的验证，叫做 `Email()`。这是从 WTForms 中提供的验证器，会确保用户输入的是合法的邮箱格式。

因为这是一个注册表单，所以通常会询问用户键入两次密码防止输错。因此我有 `password` 和 `password2` 两个字段，第二个密码字段使用了另一个验证器叫做 `EqualTo()`，这会确保第二次输入的密码和第一次输入的一致。

我还为这个类添加了两个方法叫做 `validate_username()` 和 `validate_email()`。当你以 `validate_<filed_name>` 的模式添加方法的时候，WTForms会将它们作为自定义验证器，并且在除了调用字段中定义的验证器外，还会调用这些验证函数。在这里我为了避免用户输入的用户名和邮箱在数据库中重复，因此这两个方法会在数据库中查询，如果存在相应的用户名和邮箱，则会引发一个 `ValidationError`。这个异常的参数会作为错误消息在字段旁边展示，这样用户就可以看到发生了什么。

为了在 web 页面中展示这个表单，我需要一个 HTML 模板，存储在文件 `app/templates/register.html`。这个模板和登录表单很类似：

```html
{% extends "base.html" %}

{% block content %}
    <h1>Register</h1>
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
            {{ form.email.label }}<br>
            {{ form.email(size=64) }}<br>
            {% for error in form.email.errors %}
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
        <p>
            {{ form.password2.label }}<br>
            {{ form.password2(size=32) }}<br>
            {% for error in form.password2.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
```

登录表单需要有一个链接可以让新用户前往注册页面：

```html
<p>New User? <a href="{{ url_for('register') }}">Click to Register!</a></p>
```

最后，我需要写一个处理用户注册的视图函数：

```python
from app import db
from app.forms import RegistrationForm

# ...

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
```

这个视图函数也很简单，我首先确保了用户是没有登录的。正如用户登录一样，这里的处理很相似。`if validate_on_submit()` 条件语句的逻辑就是创建一个新用户，写入到数据库，然后跳转到登录页面，这样用户就可以登录了。

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch05-register-form.png)

这样，用户就可以创建账户，登录登出了。记得尝试所有我在注册表单中加的的验证特性，以更深刻理解它们是怎么工作的。将来我会继续完善用户验证系统，比如加入修改密码等。但是现在，用户系统已经足够了，我们会去构建应用的其他部分。
