The Flask Mega-Tutorial, Part I: Hello, World!
===

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

Conda官方文档上的介绍：

>Package, dependency and environment management for any language—Python, R, Ruby, Lua, Scala, Java, JavaScript, C/ C++, FORTRAN 
>Conda is an open source package management system and environment management system that runs on Windows, macOS and Linux. Conda quickly installs, runs and updates packages and their dependencies. Conda easily creates, saves, loads and switches between environments on your local computer. It was created for Python programs, but it can package and distribute software for any language.

译者常使用conda，因为可以对多版本的Python环境进行管理，比较方便。

一些常用的命令:

- 创建Python2.7环境：`conda create pylint python=2.7 -n name`
- 创建Python3.6环境: `conda create pylint python=3.6 -n name`
- 列出目前的环境列表: `conda info -e`
- 移除环境: `conda remove --all -n name`
- 激活环境: `source activate name`
- 退出环境: `source deactivate name`