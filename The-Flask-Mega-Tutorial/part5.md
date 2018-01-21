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

