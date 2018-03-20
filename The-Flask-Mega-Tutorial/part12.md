The Flask Mega-Tutorial Part XII: Dates and Times
===

原文地址: [The Flask Mega-Tutorial Part XII: Dates and Times](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xii-dates-and-times)

这是 Flask Mega-Tutorial 第十二部分，在本章我将会告诉你如何以适应所有用户的方式来处理日期和时间，不管用户在哪里。

我的微博应用被忽视的概念之一就是日期和时间的展示。直到现在，我也只让 Python 在 User 模型里渲染 datetime 对象，而且完全忽略 Post 模型。

本章的 Github 链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.12), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.12.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.11...v0.12)

时区地狱
===

在服务器上使用 Python 来渲染向用户展示的日期和时间不是一个很好的主意。考虑下面的例子：我在 2017 年 9 月 28 日下午 4 点 06 分写了这篇文章。我的时区是 PDT(UTC-7)。运行 Python 解释器我将会得到下面的：

```
>>> from datetime import datetime
>>> str(datetime.now())
'2017-09-28 16:06:30.439388'
>>> str(datetime.utcnow())
'2017-09-28 23:06:51.406499'
```

`datetime.now()` 调用返回我当前所在地的正确时间，但是`datetime.utcnow()` 调用返回 UTC 时间。如果让全世界不同地方的人在同一时刻来运行上面的代码，那么 `datetime.now()` 函数将返回不同的结果，但是 `datetime.utcnow()` 将返回同样的结果。那么你认为在 web 应用上用哪一个时间会更好呢？

显而易见，服务器必须以持续的方式以及独立于位置的方式来管理时间。如果应用增长到需要在世界各地来部署生产服务器的话，我肯定不能让每个服务器向数据库写入不同时区的时间戳，这样的话就会导致写入的时间没法使用。因为 UTC 是最常用的标准时区并且在 datetime 类中支持，所以我将会使用它。

但是这种方法有一个重要的问题。对于不同时区的用户，使用 UTC 时间会导致他们不知道某篇文章是什么时候写的。他们需要将 UTC 时间转换成他们当地时区的时间。

从服务器角度来看将时间标准化为 UTC 时间是很有意义的，但是这样导致了用户的使用问题。本章的目标就是来解决这些问题，并且以恰当的方式来管理服务器的 UTC 时间戳。

时区转换
===

解决上面的问题一个明显的办法就是将储存的 UTC 时间转换成每个用户的本地时间。这样使得服务器仍然可以使用 UTC 时间，并且适配于每个用户的即时转换也解决了可用性问题。问题的关键在于如何知道每个用户的位置。

许多网站都有一个用户可以指定他们时区的配置页。这将会需要我添加一个页面来向用户展示时区列表。当然也可以在用户第一次访问网站的时候让他们指定时区，或者作为注册的一部分。

当然这是解决时区问题的一种优雅方式，但是这却有点奇怪，因为操作系统已经有这样的配置了。看起来直接从操作系统中提取时区信息更加高效。

正如上面提到的，web 浏览器知道用户的时区，而且通过标准的日期和时间的 JavaScript APIs 暴露出来了。有两种通过 JavaScript 来提取时区信息的方法：

- 老一点的方式是在用户第一次登录该应用的时候向服务器发送时区信息。通过 Ajax 完成，或者更加简单的方式是刷新元标识。一旦服务器知道了时区信息，它就可以在用户 session 中保存或者是写入到数据库与用户相关的实体中。从这时开始，所有的时间戳都会被调整为该时区。
- 新一点的方法是不需要在服务器上做改动，而是在本地使用 JavaScript 来完成 UTC 时间到本地时区时间的转换。

两种方式都是可以的，但是第二种方法会更好。只知道时区信息有时候并不足够以用户想要的方式来显示日期和时间。浏览器可以获取到系统的本地配置，比如指定了一些 AM/PM vs 24 小时制，DD/MM/YYYY vs MM/DD/YYYY 以及其他一些文化或者宗教风格相关的配置。

如果这些还不够，第二种方式还有一种优点就是已经有一个开源库完成了所有事情！

介绍 Moment.js 和 Flask-Moment
===

Moment.js 是一个小的开源 JavaScript 库，它会将日期和时间以其他方式渲染，其提供了所有可以想到的格式化选项。不久之前我创建了 Flask-Moment，一个小的 Flask 插件使得将 moment.js 整合到你的应用变得非常容易。

那么首先让我们安装 Flask-Moment:

```bash
(venv) $ pip install flask-moment
```

这个插件仍然是以通常的方式加入到 Flask 应用中：

```python
# ...
from flask_moment import Moment

app = Flask(__name__)
# ...
moment = Moment(app)
```

不像其他插件，Flask-Moment 是和 moment.js 一起工作的，因此应用所有的模板都必须导入这个库。为了保证该库可用，我将在 base 模板中加入该库。可以通过两种方式完成。最直接的方式是显式的加入 `<script>` 标签导入该库，但是 Flask-Moment 让这一切变得更加容易，通过暴露了一个 `moment.include_moment()` 函数来生成 `<script>` 标签：

```html
{% block scripts %}
    {{ super() }}
    {{ moment.include_moment() }}
{% endblock %}
```

添加在这里的 `scripts` 块是另一个通过 Flask-Bootstrap 基准模板导出的块。这个地方就是 JavaScript 库被导入的地方。这个块和之前的不一样，它已经在 base 模板中定义了一些内容。我想做的只是加入 moment.js 库，而不是丢掉 base 中的内容。这通过 `super()` 语句实现，它保留了 base 模板中的内容。如果你没在模板中的块使用 `super()`，那么任何在 base 模板中定义的内容将会丢失。

使用 Moment.js
===

Moment.js 使得浏览器可以使用一个 `moment` 类。渲染一个时间戳的第一步是创建一个该类的对象，以 ISO 8601 格式来传递一个时间戳。下面是一个例子:

```javascript
t = moment('2017-09-28T21:45:23Z')
```

如果你对 ISO 8601 标准格式不太熟悉的话，格式是这样的 `{{ year }}-{{ month }}-{{ day }}T{{ hour }}:{{ minute }}:{{ second }}{{ timezone }}`。我已经决定我只会使用 UTC 时区，因此最后一部分就是 Z，在 ISO 8601 格式中代表 UTC。

moment 对象提供了一些不同渲染选项的方法，下面是最常用的选项：

```javascript
moment('2017-09-28T21:45:23Z').format('L')
"09/28/2017"
moment('2017-09-28T21:45:23Z').format('LL')
"September 28, 2017"
moment('2017-09-28T21:45:23Z').format('LLL')
"September 28, 2017 2:45 PM"
moment('2017-09-28T21:45:23Z').format('LLLL')
"Thursday, September 28, 2017 2:45 PM"
moment('2017-09-28T21:45:23Z').format('dddd')
"Thursday"
moment('2017-09-28T21:45:23Z').fromNow()
"7 hours ago"
moment('2017-09-28T21:45:23Z').calendar()
"Today at 2:45 PM"
```

该例子创建了一个 moment 对象，初始化为 September 28th 2017 at 9:45pm UTC。你可以看到所有我尝试的选项，都是以 UTC-7 进行渲染的，该时区是我电脑的配置。你可以在你的浏览器控制台上输入上面的命令，但是得确保你已经在控制台导入了 moment.js。你可以在 [https://momentjs.com/](https://momentjs.com/) 来测试。

注意不同的格式方法会有不同的表现。`format()` 方法通过传入的格式字符串控制了输出的格式，就和 Python 中的 strftime 函数一样。`fromNow()` 和 `calendar()` 方法根据当前时间来渲染时间戳，因此你可以得到像 `一分钟前` 或者 `两小时后` 这样的输出。

如果你直接使用 JavaScript，上面的调用就会返回渲染后的时间戳字符串。是否将输出插入到页面合适的地方取决于你，这样做需要使用 JavaScript 来操作 DOM。Flask-Moment 插件极大的简化了 moment.js 的使用，通过启用一个 moment 对象，就和 JavaScript 中一样。

让我们看看在个人信息页面中出现的时间戳。现有的 `user.html` 模板让 Python 生成时间的字符串表示。我现在可以使用 Flask-Moment 来渲染时间戳了：

```html
{% if user.last_seen %}
<p>Last seen on: {{ moment(user.last_seen).format('LLL') }}</p>
{% endif %}
```

你可以看到，Flask-Moment 和 JavaScript 库的语法很像，一个不同是传递到 `moment()` 函数的参数现在是 Python datetime 对象而不是 ISO 8601 字符串。在模板中调用 `moment()` 会自动生成对应的 JavaScript 代码并且将渲染的时间戳插入到 DOM 合适的地方。

另外一个使用到 Flask-Moment 和 moment.js 的地方是 `_post.html` 子模板，它会在首页和用户页面进入。当前版本的模板，每一个文章之前都有一个 `username says:` 行。现在我可以添加一个由 `fromNow()` 渲染的时间戳了：

```html
<a href="{{ url_for('user', username=post.author.username) }}">
    {{ post.author.username }}
</a>
said {{ moment(post.timestamp).fromNow() }}:
<br>
{{ post.body }}
```

下面你可以看到最后的渲染结果：

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch13-moment.png)
