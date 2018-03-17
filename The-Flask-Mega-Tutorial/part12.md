The Flask Mega-Tutorial Part XII: Dates and Times
===

原文地址: [The Flask Mega-Tutorial Part XII: Dates and Times](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xii-dates-and-times)

这是 Flask Mega-Tutorial 第十二部分，在本章我将会告诉你如何以适应所有用户的方式来处理日期和时间，不管用户在哪里。

我的微博应用被忽视的概念之一就是日期和时间的展示。直到现在，我也只让 Python 在 User 模型里渲染 datetime对象，而且完全忽略 Post 模型。

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

