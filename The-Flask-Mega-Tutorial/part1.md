The Flask Mega-Tutorial, Part I: Hello, World!
===

原文地址: [The Flask Mega-Tutorial, Part I: Hello, World!](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

欢迎！你现在正要开始一段学习如何使用Python和Flask框架来创建web应用的旅程。上面的视频提供了本教程的预览。在第一章，你讲学习到如何开始一个Flask项目。在本章结束，你的电脑上将会有一个简单的Flask web应用在运行。

注意：

1. 如果你在寻找这个教程的老版本，[在这里](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world-legacy)
2. 如果你想在这个博客中支持我的工作，或者等不及每周才更新的文章，我提供了这个教程打包为ebook以及视频集的完整版本。获取更多的信息，访问[learn.miguelgrinberg.com](learn.miguelgrinberg.com)

在这个教程中出现的所有代码示例都托管在Github仓库中。从Github上下载代码省去了你敲代码的时间，但是我还是强烈建议你自己敲代码，至少在前几章中。一旦你对Flask和示例应用更加熟悉了，如果打字太过乏味，你就可以直接从Github中拉取代码。

在每章的开始，我将提供你三个在这章很有用的Github链接。`Browse`链接将会打开Microblog的Github仓库，这里会显示你正在阅读的章节添加了哪些变化，但不会添加后面章节的变化。`Zip`链接是包含整个应用以及当前章节的变化的zip下载链接。`Diff`链接将会打开一个你可以看到本章做了何许变化的视图表示。

本章的Github链接是: [Browse](https://github.com/miguelgrinberg/microblog/tree/v0.1), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.1.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.0...v0.1).

安装Python
===

如果你电脑上没有装Python，那么现在就去装一个。你可以在[Python官方网站](http://python.org/download/)下载。

为了保证你的Python安装成功，你可以打开一个终端窗口然后键入`python3`或者`python`。下面是你应该会看到的:

```
$ python3
Python 3.5.2 (default, Nov 17 2016, 17:05:23)
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> _
```

Python解释器现在正在交互的提示符处等待输入，你可以键入Python语句。在后面的章节你会学习到这个交互提示符在那些方面会有用。要退出交互式界面，键入`exit()`并且按下Enter。在Linux或者Mac OS X上你也可以键入Ctrl-D来退出解释器。在Windows上，退出快捷键是Ctrl-Z然后按下Enter.

安装Flask
===

下一步是安装Flask，再次之前我想告诉你安装Python包的最佳实践。

在Python中，类似于Flask的包都是可以从一个公共仓库中获取的，任何人都可以下载并且安装这些包。官方的Python包仓库是[PyPI](https://pypi.python.org/pypi)，表示Python Package Index(一些人也把这个仓库叫做cheese shop)。从PyPI中安装包是非常简单的，因为Python提供了一个pip工具来进行下载安装和管理的(在Python2.7需要单独下载pip)。

你可以通过以下方式来安装包: `$ pip install <package-name>`

不过一般情况下这样安装不会成功也不合适，如果你的Python解释器是在全局安装的，那么你作为普通用户将没有权限来修改它。因此唯一的方式是切换到管理员账户来安装这些包。即使忽略上面的情况，那么我们来考虑下载你安装一个包的时候会发生什么。pip工具将会从PyPI中下载包，然后将其安装。从那时起，每个Python脚本如果需要的话都会载入这个包。想象一下如果你以Flask0.11版本完成了一个web应用。但是现在Flask更新了，到0.12了。你开始了一个新项目，使用0.12版本，但是如果你在全局用0.12版本替换0.11版本，那么之前写的web应用就有可能无法正常运行。最好的方式是，一个应用使用一个版本。

Python使用一个叫虚拟环境的概念来解决这一问题。一个虚拟环境是一个Python解释器的完整拷贝。当你在虚拟环境中安装包，系统级的Python将不会收到影响，只有这个虚拟环境中会安装。因此每一个应用使用不同的虚拟环境，就有完全的自由去安装想安装的任何包。并且虚拟环境是被创建这个环境的用户所有，因此也不需要管理员权限。

首先我们为我们的项目创建一个目录`microblog`，也是我们应用的名字。

```
$ mkdir microblog
$ cd microblog
```

如果你使用Python3，就已经包含了虚拟环境这一功能：`python3 -m venv venvname`

通过这一个命令，我请求Python运行`venv`包，将会创建一个虚拟环境名字是`venvname`。这时候我在项目目录中创建了一个虚拟环境，名字是`venvname`，因此无论什么时候我进入项目目录，我都可以找到相应的虚拟环境。这个`venvname`文件夹下面就包含了所有的虚拟环境相关文件。

如果你使用了Python 3.4之前的版本，你需要下载并且安装一个第三方工具叫做`virtualenv`，你可以使用下面的命令来创建一个虚拟环境: `virtualenv venv`

现在你可以激活你创建的虚拟环境了，使用以下命令：`$ source venvname/bin/activate`

如果你使用Windows，那么应该这样：`$ venv\Scripts\activate`

当你激活了虚拟环境，你的终端会话的配置将被改变，这样当你键入`python`命令的时候，调用的是你虚拟环境立的Python解释器。而且终端提示符上也加入了虚拟环境的名字。所有的改变都是临时的，而且只是针对当前会话的，所以当你关闭终端窗口的时候，这些也就不存在了，这样你就可以在多个终端窗口中激活不同的虚拟环境。

这时你就可以在当前虚拟环境中安装Flask了：`(venv) $ pip install flask`

如果你想确认Flask是否成功安装，你可以打开Python解释器然后键入`import Flask`:

```
>>> import flask
>>> _
```

如果没有报任何错，那么恭喜你，Flask已经成功安装。

`[译者注]` 使用Conda对Python环境进行管理
---

[Conda官方文档](https://conda.io/)上的介绍：

> Package, dependency and environment management for any language—Python, R, Ruby, Lua, Scala, Java, JavaScript, C/ C++, FORTRAN 
> 
> Conda is an open source package management system and environment management system that runs on Windows, macOS and Linux. Conda quickly installs, runs and updates packages and their dependencies. Conda easily creates, saves, loads and switches between environments on your local computer. It was created for Python programs, but it can package and distribute software for any language.

译者常使用conda，因为可以对多版本的Python环境进行管理，比较方便。

一些常用的命令:

- 创建Python2.7环境：`conda create pylint python=2.7 -n name`
- 创建Python3.6环境: `conda create pylint python=3.6 -n name`
- 列出目前的环境列表: `conda info -e`
- 移除环境: `conda remove --all -n name`
- 激活环境: `source activate name`
- 退出环境: `source deactivate name`

一个"Hello World"的Flask应用
===

如果你去[Flask官方网站](http://flask.pocoo.org/)，你可以发现只有五行代码的非常简单的例子。我在这里将会给你展示一个可以写更大应用程序的基础结构的例子。

应用将会在一个package中存在。在Python中，一个包含`__init__.py`的子目录被认为是一个package，也是可以被导入(import)的。当你导入一个包的时候，`__init__.py`会运行然后定义那些package向外部暴露的变量或者定义。

让我们创建一个package叫做`app`，这个package会承载Flask应用。确保你在`microblog`目录下，然后执行下面的命令。`(venv) $ mkdir app`

然后`__init__.py`将包含下面的代码：

```
from flask import Flask

app = Flask(__name__)

from app import routes
```

上面的代码首先从flask包中导入了Flask类，然后创建了一个Flask对象`app`。`__name__`变量是Python预定义的变量，它的值是目前正在使用的Python模块的名字。Flask使用这个模块的路径作为载入其他资源比如模板文件的基准路径。在所有情况下，传递`__name__`总是正确配置Flask的方式。然后应用导入`routes`模块，但是现在还没有创建。

目前来看有一个概念是比较易混淆的，就是有两个实体叫做`app`。app包是通过app目录和`__init__.py`脚本定义的，可以通过`from app import routes`来引用。app变量是定义在`__init__.py`中Flask类的一个实例，它是app包的一个成员。

另一个特点是routes模块在最底下导入，而不是最上面。这样做的目的是为了避免循环导入。后面你会看到routes模块需要在`__init__.py`中定义的app变量。因此将类似这样的模块放在在最后面导入可以避免因为两个文件相互引用而导致的错误。

那么routes模块中包含什么呢？routes(路由)是应用实现的不同的URLs。在Flask中，应用的路由是由Python函数来处理的，叫做视图函数。视图函数会映射到一个或者多个路由URL上，这样Flask就知道对于客户端给定的URL该怎么处理。

这是你的第一个视图函数，你需要写在新的模块`app/routes.py`中:

```
from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
```

这个视图函数其实很简单，这是返回了这个`Hello, World!`字符串。在函数定义上面的是两个装饰器，Python中特别的语法糖。装饰器改变或者增加了被装饰函数的功能。一个装饰器经常会用到的地方是将函数注册为某些事件的回调函数。在这里，`@app.route`装饰器创建了以参数给定的URL和视图函数的联系。这里有两个装饰器，将`/`和`/index`和index函数关联起来了。这意味着，不论web浏览器向哪个URL发送请求，Flask将会调用这个函数，然后将返回值作为对浏览器的响应。

为了完成这个应用，你需要有一个顶层的Python脚本来定义Flask应用实例。名字就定义为`microblog.py`，用单独的一句来导入这个应用实例。`from app import app`

还记得这两个`app`实体吗？Flask实例app是app包的一个成员。下面你可以看到整个项目的目录结构：

```
microblog/
  venv/
  app/
    __init__.py
    routes.py
  microblog.py
```

另外Flask需要被告知如何去导入应用——通过`FLASK_APP`环境变量：`(venv) $ export FLASK_APP=microblog.py`

如果你使用Windows，则使用`set`而不是`export`。

完成上述步骤之后，你就可以启动应用了！

```
(venv) $ flask run
 * Serving Flask app "microblog"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

在服务器初始化完成之后，它就在等待来自客户端的链接了。`flask run`的输出表示服务器正在运行在`127.0.0.1`这个IP地址上，这个总是你本机的地址。这个地址很常用，因此有一个更简单的别名:`localhost`。服务器会监听特定的端口，在生产环境上的服务器一般会监听443端口，或者在不需要加密的时候使用80端口，但是这些都需要管理员权限。因为应用在开发环境上运行，Flask使用了可用的5000端口。下面在浏览器中输入下面的URL：`http://localhost:5000/`，当然你也可以输入下面这个: `http://localhost:5000/index`

两个不同的URL会返回同样的东西。但是你输入其他URL将会发生一个404错误，因为只有上面两个URL可以被应用识别。

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch01-hello-world.png)

然后你可以按下Ctrl-C来停止服务器。

恭喜你，你已经完成了作为web开发者的第一步！