The Flask Mega-Tutorial Part III: Web Forms
===

原文地址: [The Flask Mega-Tutorial Part III: Web Forms](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms)

这是Flask Mega-Tutorial系列的第三部分，我将带你学习web表单(forms)

在第二部分，我为应用首页创建了一个简单的模板，而且使用了模拟对象作为目前还没有的东西的替代品，比如用户或者文章对象。在这章我将要解决的是目前应用存在的诸多问题之一，如何通过web表单来接受用户的输入。

Web表单是任何web应用中最基本的组成构件之一。我将使用表单来允许用户提交文章以及登录应用。

在开始这章之前，确保你已经拥有上一章完成的应用，并且运行没有错误。

本章的Github链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.3), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.3.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.2...v0.3)

Flask-WTF简介
===

为了处理应用中的web表单，我使用了[Flask-WTF](http://packages.python.org/Flask-WTF)扩展，它是对[WTForms](https://wtforms.readthedocs.io/)的简单封装并与Flask很好的整合在一起。这是我向你展示的第一个Flask扩展，但不是最后一个。在Flask生态系统中，扩展是非常重要的一部分，它们提供了Flask有意没有处理的问题的解决方案。

Flask扩展也是普通的Python包，可以使用pip来安装。你可以用以下命令在虚拟环境中安装`Flask-WTF`: `pip install flask-wtf`

配置
===

因为现在应用很简单，因此我不需要担心它的配置问题。但是对于除过这个最简单的其他任何应用来说，你将发现Flask(以及你使用的Flask扩展)会提供一定的自由度，你需要来向框架传递一个配置变量的列表来决定怎么做。

应用有几种指定配置选项的格式。最基本的是以`app.config`的键(key)的形式定义变量，它使用了字典的风格来定义变量。比如，你可以这样：

```
app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
# ... add more variables here as needed
```

虽然上面的方式已经足够来为Flask创建配置选项，但是我更乐意去实现关注点分离原则(the principle of separation of concerns)，所以与其将我的配置和创建应用放在一起，不如我使用一个稍微复杂的结构来将我的配置文件放在单独的文件里。

我非常喜欢使用一个类来储存配置，是因为它非常容易扩展。为了更好的组织，我将会在一个单独的Python模块中创建这个配置类。下面你可以看到为应用创建的新的配置类，存储在顶层目录的`config.py`模块中。

```
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
```

非常简单对吧？配置现在是以类属性的方式定义在`Config`类中的。如果应用需要更多的配置项，那么可以继续添加到类中。如果后面我需要再创建配置集合，我可以创建`Config`的子类。但是目前先不用考虑它。

目前唯一配置的`SECRET_KEY`配置变量在大多数Flask应用中都是非常重要的一部分。Flask和其他一些扩展会使用这个值作为加密密钥用于生成签名或者令牌。Flask-WTF使用它来保护web表单免于[Cross-Site Request Forgery](http://en.wikipedia.org/wiki/Cross-site_request_forgery) - CSRF的攻击(发音为seasurf)。顾名思义，secret key应该是私密的，其生成的令牌和签名的安全程度取决于除了应用的维护者之外没有人知道。

这个值的赋值语句分为两部分，通过`or`操作符连接在一起。第一部分是查找一个也叫作`SECRET_KEY`的环境变量。第二部分，是一个硬编码字符串。这种模式在后面很多配置赋值的时候都会用到，首先去读取环境变量的值，如果没有，则使用硬编码字符串作为替代。当你开发这个应用的时候，没有太高的安全需求，所以你可以直接使用这个硬编码字符串。但是如果应用部署在生产服务器上，我将会在环境变量中设置相应的值以保证安全。

现在我已经有了配置文件，我需要告知Flask读取并且应用配置。这可以通过使用`app.config.from_object()`方法来完成：

```
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes
```

上面`config`是Python模块，而`Config`(uppercase "C")是这个Python模块中的类。

正如我上面提到的，配置项可以使用字典语法来从`app.config`读取。下面展示了我如何读取secret key的：

```
>>> from microblog import app
>>> app.config['SECRET_KEY']
'you-will-never-guess'
```
