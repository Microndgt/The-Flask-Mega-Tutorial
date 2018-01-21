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
2. `is_active`: 如果用户账户是活跃的则为True, 否则为 False
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
