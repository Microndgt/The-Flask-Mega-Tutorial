The Flask Mega-Tutorial, Part I: Hello, World!
===

原文地址: [The Flask Mega-Tutorial, Part I: Hello, World!](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

欢迎！你现在正要开始一段学习如何使用 Python 和 Flask 框架来创建 web 应用的旅程。上面的视频提供了本教程的预览。在第一章，你将学习如何开始一个 Flask 项目。在本章结束，将会有一个简单的 Flask web 应用在你的电脑运行。

注: 视频请查看原文。

注意：

1. 如果你在寻找这个教程的老版本，[在这里](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world-legacy)
2. 如果你想在这个博客中支持我的工作，或者等不及每周才更新的文章，我提供了打包为 ebook 的教程以及视频集的完整版本。获取更多的信息，访问[learn.miguelgrinberg.com](https://learn.miguelgrinberg.com/)

教程中出现的所有代码都托管在 Github 仓库中。从 Github 上下载代码省去了你敲代码的时间，但是我还是强烈建议你自己敲代码，至少在前几章中。一旦你对 Flask 和示例应用更加熟悉了，如果打字太过乏味，你就可以直接从 Github 中拉取代码。

在每章的开始，我将提供给你三个在这章很有用的 Github 链接。`Browse` 链接将会打开 Microblog 的 Github 仓库，这里会显示你正在阅读的章节添加了哪些变化，但不包含后面章节的变化。`Zip` 链接包含整个应用以及当前章节的变化的 zip 下载链接。打开 `Diff` 链接可以看到本章做了何许变化的视图表示。

本章的 Github 链接是: [Browse](https://github.com/miguelgrinberg/microblog/tree/v0.1), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.1.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.0...v0.1).

安装 Python
===

如果你电脑上没有装 Python，那么现在就去装一个。你可以在[Python 官方网站](http://python.org/download/)下载。

为了保证你的 Python 安装成功，你可以打开一个终端窗口然后键入 `python3` 或者 `python`。下面是你应该会看到的:

```shell
$ python3
Python 3.5.2 (default, Nov 17 2016, 17:05:23)
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> _
```

Python 解释器现在正在交互的提示符处等待输入，你可以键入 Python 语句。在后面的章节你会学习到这个交互提示符在那些方面会有用。要退出交互式界面，键入 `exit()` 并且按下 Enter。在 Linux 或者 Mac OS X 上你也可以键入 Ctrl-D 来退出解释器。在 Windows 上，退出快捷键是 Ctrl-Z 然后按下 Enter.

安装 Flask
===

下一步是安装 Flask，再次之前我想告诉你安装 Python 包的最佳实践。

在 Python 中，类似于 Flask 的包都是可以从一个公共仓库中获取的，任何人都可以下载并且安装这些包。官方的 Python 包仓库是[PyPI](https://pypi.python.org/pypi)，表示 Python Package Index(一些人也把这个仓库叫做 cheese shop)。从 PyPI 中安装包是非常简单的，因为 Python 提供了一个 pip 工具来进行下载安装和管理的(在 Python2.7 需要单独下载 pip)。

你可以通过以下方式来安装包: `$ pip install <package-name>`

不过一般情况下这样安装不会成功也不合适，如果你的 Python 解释器是在全局安装的，那么你作为普通用户将没有权限来修改它。因此唯一的方式是切换到管理员账户来安装这些包。即使忽略上面的情况，那么我们来考虑下载你安装一个包的时候会发生什么。pip 工具将会从 PyPI 中下载包，然后将其安装。从那时起，每个 Python 脚本如果需要的话都会载入这个包。想象一下如果你以 Flask0.11版本完成了一个 web 应用。但是现在 Flask 更新了，到 0.12 了。你开始了一个新项目，使用 0.12 版本，但是如果你在全局用 0.12 版本替换 0.11 版本，那么之前写的 web 应用就有可能无法正常运行。最好的方式是，一个应用使用一个版本。

Python 使用一个叫虚拟环境的概念来解决这一问题。一个虚拟环境是一个 Python 解释器的完整拷贝。当你在虚拟环境中安装包，系统级的 Python 将不会收到影响，只有这个虚拟环境中会安装。因此每一个应用使用不同的虚拟环境，就有完全的自由去安装想安装的任何包。并且虚拟环境是被创建这个环境的用户所有，因此也不需要管理员权限。

首先我们为我们的项目创建一个目录 `microblog`，也是我们应用的名字。

```shell
$ mkdir microblog
$ cd microblog
```

如果你使用 Python3，就已经包含了虚拟环境这一功能：`python3 -m venv venvname`

通过这一个命令，我请求 Python 运行 `venv` 包，将会创建一个虚拟环境名字是 `venvname`。这时候我在项目目录中创建了一个虚拟环境，名字是 `venvname`，因此无论什么时候我进入项目目录，我都可以找到相应的虚拟环境。这个 `venvname` 文件夹下面就包含了所有的虚拟环境相关文件。

如果你使用了 Python 3.4 之前的版本，你需要下载并且安装一个第三方工具叫做 `virtualenv`，你可以使用下面的命令来创建一个虚拟环境: `virtualenv venv`

现在你可以激活你创建的虚拟环境了，使用以下命令：`$ source venvname/bin/activate`

如果你使用 Windows，那么应该这样：`$ venv\Scripts\activate`

当你激活了虚拟环境，你的终端会话的配置将被改变，这样当你键入 `python` 命令的时候，调用的是你虚拟环境立的 Python 解释器。而且终端提示符上也加入了虚拟环境的名字。所有的改变都是临时的，而且只是针对当前会话的，所以当你关闭终端窗口的时候，这些也就不存在了，这样你就可以在多个终端窗口中激活不同的虚拟环境。

这时你就可以在当前虚拟环境中安装 Flask 了：`(venv) $ pip install flask`

如果你想确认 Flask 是否成功安装，你可以打开 Python 解释器然后键入 `import Flask`:

```shell
>>> import flask
>>> _
```

如果没有报任何错，那么恭喜你，Flask 已经成功安装。

`[译者注]` 使用 Conda 对 Python 环境进行管理
---

[Conda 官方文档](https://conda.io/)上的介绍：

> Package, dependency and environment management for any language—Python, R, Ruby, Lua, Scala, Java, JavaScript, C/ C++, FORTRAN 
> 
> Conda is an open source package management system and environment management system that runs on Windows, macOS and Linux. Conda quickly installs, runs and updates packages and their dependencies. Conda easily creates, saves, loads and switches between environments on your local computer. It was created for Python programs, but it can package and distribute software for any language.

译者常使用 conda，因为可以对多版本的 Python 环境进行管理，比较方便。

一些常用的命令:

- 创建 Python2.7环境：`conda create pylint python=2.7 -n name`
- 创建 Python3.6环境: `conda create pylint python=3.6 -n name`
- 列出目前的环境列表: `conda info -e`
- 移除环境: `conda remove --all -n name`
- 激活环境: `source activate name`
- 退出环境: `source deactivate name`

一个"Hello World"的 Flask 应用
===

如果你去[Flask 官方网站](http://flask.pocoo.org/)，你可以发现只有五行代码的非常简单的例子。我在这里将会给你展示一个可以写更大应用程序的基础结构的例子。

应用将会在一个 package 中存在。在 Python 中，一个包含 `__init__.py` 的子目录被认为是一个 package，也是可以被导入(import)的。当你导入一个包的时候，`__init__.py` 会运行然后定义那些 package 向外部暴露的变量或者定义。

让我们创建一个 package 叫做 `app`，这个 package 会承载 Flask 应用。确保你在 `microblog` 目录下，然后执行下面的命令。`(venv) $ mkdir app`

然后 `__init__.py` 将包含下面的代码：

```python
from flask import Flask

app = Flask(__name__)

from app import routes
```

上面的代码首先从 flask 包中导入了 Flask 类，然后创建了一个 Flask 对象 `app`。`__name__` 变量是 Python 预定义的变量，它的值是目前正在使用的 Python 模块的名字。Flask 使用这个模块的路径作为载入其他资源比如模板文件的基准路径。在所有情况下，传递 `__name__` 总是正确配置 Flask 的方式。然后应用导入 `routes` 模块，但是现在还没有创建。

目前来看有一个概念是比较易混淆的，就是有两个实体叫做 `app`。app 包是通过 app 目录和 `__init__.py` 脚本定义的，可以通过 `from app import routes` 来引用。app 变量是定义在 `__init__.py` 中 Flask 类的一个实例，它是 app 包的一个成员。

另一个特点是 routes 模块在最底下导入，而不是最上面。这样做的目的是为了避免循环导入。后面你会看到 routes 模块需要在 `__init__.py` 中定义的 app 变量。因此将类似这样的模块放在在最后面导入可以避免因为两个文件相互引用而导致的错误。

那么 routes 模块中包含什么呢？routes(路由)是应用实现的不同的 URLs。在 Flask 中，应用的路由是由 Python 函数来处理的，叫做视图函数。视图函数会映射到一个或者多个路由 URL 上，这样 Flask 就知道对于客户端给定的 URL 该怎么处理。

这是你的第一个视图函数，你需要写在新的模块 `app/routes.py` 中:

```python
from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
```

这个视图函数其实很简单，这是返回了这个 `Hello, World!` 字符串。在函数定义上面的是两个装饰器，Python 中特别的语法糖。装饰器改变或者增加了被装饰函数的功能。一个装饰器经常会用到的地方是将函数注册为某些事件的回调函数。在这里，`@app.route` 装饰器创建了以参数给定的 URL 和视图函数的联系。这里有两个装饰器，将 `/` 和 `/index` 和 index 函数关联起来了。这意味着，不论 web 浏览器向哪个 URL 发送请求，Flask 将会调用这个函数，然后将返回值作为对浏览器的响应。

为了完成这个应用，你需要有一个顶层的 Python 脚本来定义 Flask 应用实例。名字就定义为 `microblog.py`，用单独的一句来导入这个应用实例。`from app import app`

还记得这两个 `app` 实体吗？Flask 实例 app 是 app 包的一个成员。下面你可以看到整个项目的目录结构：

```
microblog/
  venv/
  app/
    __init__.py
    routes.py
  microblog.py
```

另外 Flask 需要被告知如何去导入应用——通过 `FLASK_APP` 环境变量：`(venv) $ export FLASK_APP=microblog.py`

如果你使用 Windows，则使用 `set` 而不是 `export`。

完成上述步骤之后，你就可以启动应用了！

```shell
(venv) $ flask run
 * Serving Flask app "microblog"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

在服务器初始化完成之后，它就在等待来自客户端的链接了。`flask run` 的输出表示服务器正在运行在 `127.0.0.1` 这个 IP 地址上，这个总是你本机的地址。这个地址很常用，因此有一个更简单的别名: `localhost`。服务器会监听特定的端口，在生产环境上的服务器一般会监听 443 端口，或者在不需要加密的时候使用 80 端口，但是这些都需要管理员权限。因为应用在开发环境上运行，Flask 使用了可用的 5000 端口。下面在浏览器中输入下面的 URL：`http://localhost:5000/`，当然你也可以输入下面这个: `http://localhost:5000/index`

两个不同的 URL 会返回同样的东西。但是你输入其他 URL 将会发生一个 404 错误，因为只有上面两个 URL 可以被应用识别。

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch01-hello-world.png)

然后你可以按下 Ctrl-C 来停止服务器。

恭喜你，你已经完成了作为 web 开发者的第一步！