The Flask Mega-Tutorial Part IX: Pagination
===

原文地址: [The Flask Mega-Tutorial Part XIV: Ajax](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiv-ajax)

这是 Flask Mega-Tutorial 第十四部分，在本章我将会演示如何添加一个实时的语言翻译功能，使用了微软的翻译服务和一些 JavaScript。

在本章，我将离开服务端的开发，致力于和服务端同等重要的客户端组件功能。你看到过一些站点在用户生成内容旁边的翻译链接了吗？这些链接都会触发一个实时的内容翻译。翻译好的内容会显示在原有内容的下面。谷歌会在外文搜索页面显示它，Facebook 的博文，Twitter 的 tweets 都会显示。下来我会向你展示如何添加一个非常类似的功能到我们的微博上。

本章的 Github 链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.14), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.14.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.13...v0.14)

服务端 VS 客户端
===

在我已经遵循了很久的传统服务端模型中，有一个客户端(用户使用的 web 浏览器)会发起 HTTP 请求到应用服务器上。一个请求可以简单的请求 HTML 页面，比如你点击的 Profile 链接，或者触发一个动作，比如在你编辑个人信息之后的提交按钮。两种请求类型，服务器都是通过发送给客户端一个新的 web 页面来完成请求的，不论是直接的还是重定向的。客户端则会使用新的页面来替换旧的页面。这种循环一直进行，只要用户还在该应用的站点上。在这种模型里，服务端完成了所有工作，而客户端只是显示 web 页面并且允许用户输入。

还有一种不同的模型，这种模型里客户端会扮演更加活跃的角色，客户端会发起请求，服务端会响应一个 web 页面，但是不同于之前的例子，并不是所有的页面数据都是 HTML，页面的有些部分是代码，一般是以 JavaScript 写的。一旦客户端接收到页面之后就会显示出 HTML 部分，并且执行代码。从现在开始你就有一个可用的客户端，它会很少甚至不和服务器交互。在一个严格的客户端应用里，首先下载整个应用，然后应用就在客户机上运行，只有在提取或者存储数据以及对 web 页面外观做动态更改的时候才会和服务端交互。这种应用被称作单页应用或者 SPAs。

大多数应用是这两种模型的混合体，使用了两者的技术。我的微博应用基本上是一个服务器端应用，但是现在我将要给它增加一些客户端动作。为了给用户微博做实时的翻译，客户浏览器将会给服务器发送异步请求，服务器的响应会导致客户端进行页面刷新。客户端就会将翻译动态的插入到当前页面。这种技术被称为 Ajax，是 Asynchronous JavaScript and XML 的缩写(目前 XML 基本上被 JSON 所代替)。

实时翻译工作流
===

幸亏有 Flask-Babel 使得应用对于外文有良好的支持，这样我可以将微博翻译成尽可能多的语言称为可能。当然，忽略了一点。用户一般是用他们自己的语言书写微博，因此很有可能用户会遇到一篇完全不知道什么语言写的微博。自动翻译的质量现在仍然不够好，但是在大多数你只想知道文本的大概意思的情况下已经很不错了。

这是一个使用 Ajax 服务实现的理想功能。考虑到首页或者探索页会显示多个微博，一些可能是以外文书写的。如果我使用传统的服务器端技术实现翻译，那么可能会导致原始页面会被新的页面替代。事实上在诸多微博中翻译一篇并不是一个足够大的动作需要整个页面进行更新，如果能够在原始文本下动态插入翻译的文章而不影响页面其他部分会是最好的。

实现实时自动翻译需要这几步。第一，我需要确定文本使用什么语言去翻译。而且我需要知道每个用户常用语言，因为我想在用户没有使用的语言旁边显示翻译链接。当用户点击翻译链接的时候，我需要给服务器发送 Ajax 请求，之后服务器会调用第三方的翻译 API。一旦服务器返回翻译后的文章，客户端 JavaScript 代码会动态的将文本插入到页面。你应该可以发现，这有一些比较重要的问题，下来我们会一个个解释。

语言辨别
===

第一个问题是要辨别一个微博是用什么语言写的。这并不是严格上的科学问题，但是并不能总是清晰的检测一门语言，不过在大多数情况下，自动检测工作都还不错。在 Python 里，有一个很好的语言检测包叫做 `guess_language`。这个包的原始版本太老了，而且没有支持 Python3。因此我安装一个衍生版本同时支持 Python2 和 3。

```shell
(venv) $ pip install guess-language_spirit
```

计划是将每一篇微博都输入到这个包里，然后检测其语言。因为这样的分析是耗时的，我不想做重复工作，因此我会在微博提交的时候来设置语言。检测到的语言将会存储在 posts 表中。

第一步是在 `Post` 模型中添加一个 `language` 字段

```python
class Post(db.Model):
    # ...
    language = db.Column(db.String(5))
```

在每次修改模型之后，都需要一个数据库迁移脚本

```shell
(venv) $ flask db migrate -m "add language to posts"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added column 'post.language'
  Generating migrations/versions/2b017edaa91f_add_language_to_posts.py ... done
```

之后应用这个数据库迁移脚本

```shell
(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Upgrade ae346256b650 -> 2b017edaa91f, add language to posts
```

我现在就可以在微博提交的时候检测和存储语言信息了：

```python
from guess_language import guess_language

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        # ...
```

这样在每次微博提交之后，我都会运行 `guess_language` 函数来检测语言。如果语言返回是 UNKNOWN 或者我得到了一个非预期比较长的结果，我会在数据库存储一个空字符串。我将假定任何微博的语言字段为空字符串，则该微博语言为 UNKNOWN.

显示翻译链接
===

第二步很简单。我要做的是在不是当前用户使用语言的微博旁边加上翻译链接。

```html
{% if post.language and post.language != g.locale %}
    <br><br>
    <a href="#">{{ _('Translate') }}</a>
{% endif %}
```

我加在 `_post.html` 子模板上，因此翻译功能将会出现在任何显示的微博上。翻译链接只有在该微博语言被检测到，并且该语言不匹配通过 Flask-Babel 的 localeselector 装置器装饰的函数选择的语言的时候才会出现。回忆在第十三章，选择的地区信息存储在 `g.locale`。链接的文本需要能被 Flask-Babel 翻译的形式添加，因此我使用了 `_()` 函数。

注意到我现在还没有为这个链接绑定动作。首先我想弄明白如何执行真实的翻译。

使用第三方的翻译服务
===

两大主要的翻译服务是 [Google Cloud Translation API](https://developers.google.com/translate/) 和 [Microsoft Translator Text API](http://www.microsofttranslator.com/dev/)。两者都是付费服务，但是微软提供了可选的层级，低层级的翻译是免费的。谷歌以前提供过免费翻译服务，但是现在即使最低层级的服务都是收费的。因为我现在只是想使用翻译进行试验而不想花钱，因此我会选择微软的解决方案。

在你可以使用微软翻译 API 之前，你需要获得一个 [Azure](https://azure.com/) 账户 —— 微软云服务。你可以选择免费层级，但是需要提供信用卡号，如果你一直在免费层级，你的卡就不会被消费。

一旦你有了 Azure 账户，前往 Azure 首页并且点击左上的 New 按钮，然后输入或者选择 `Translator Text API`。当我点击 Create 按钮，会出现一个可以定义新的翻译器资源的表单。你可以在下面看到我是如何完成表单的：

![](https://blog.miguelgrinberg.com/static/images/mega-tutorial/ch15-azure-translator.png)

当你再次点击 Create 按钮，你的账户将会添加一个翻译器 API 源。几秒钟之后，你将会在顶部收到一条翻译器源已经部署的消息。点击 Go to resource 按钮，然后点击 Keys 选项，你将会看到两个键，Key 1 和 Key 2.将任一个键复制然后输入到终端的环境变量里(如果你使用 Windows，使用 set 而不是 export)

```shell
(venv) $ export MS_TRANSLATOR_KEY=<paste-your-key-here>
```

键用来在翻译服务里认证，因此需要添加到应用配置里。

```python
class Config(object):
    # ...
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
```

我更喜欢将配置写在环境变量里然后在这里将其导入到 Flask 的配置系统里。在有敏感信息，比如键或者密码的时候比较重要。你肯定不想将这些信息显式的写在代码里。

微软的翻译器 API 是一个 web 服务，它接收 HTTP 请求。有多个 Python HTTP 客户端，最流行并且好用的是 `requests` 包。因此在虚拟环境中安装它：

```shell
(venv) $ pip install requests
```

下面你可以看到我使用微软翻译器 API 进行翻译的代码。我将它放在了新的 `app/translate.py` 模块里：

```python
import json
import requests
from flask_babel import _
from app import app

def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in app.config or \
            not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    auth = {'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY']}
    r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
                     '/Translate?text={}&from={}&to={}'.format(
                         text, source_language, dest_language),
                     headers=auth)
    if r.status_code != 200:
        return _('Error: the translation service failed.')
    return json.loads(r.content.decode('utf-8-sig'))
```

这个函数使用要翻译的文本，源语言以及目标语言作为参数，并且返回一个翻译后的文本。首先检查是否有相应翻译服务的配置，如果没有的话，会返回一个错误。错误也是一个字符串，所以从外界来看，就像是翻译后的文本。这样确保了即使出现错误，那么用户也能看到有意义的错误信息。

requests 包的 `get()` 方法发送一个 GET 方法的 HTTP 请求，使用给定的 URL 作为第一个参数。我使用了 `v2/Ajax.svc/Translate` URL，它是翻译服务提供的，并且返回 JSON 形式的翻译文本。文本，源语言以及目标语言都需要以 URL 查询参数的方式给定，分别是 text, from 和 to。为了进行身份验证，我需要将配置中的 Key 传递过去。这个 Key 需要以自定义 HTTP 头的方式发送，名字是 `Ocp-Apim-Subscription-Key`。我创建了 auth 字典，并且将它传递给 requests 的 headers 参数。

`requests.get()` 方法返回一个响应对象，包含了服务提供的所有细节。我首先检查返回状态码是不是 200，该状态码代表依次成功的请求。如果我得到其他状态码，我就知道发生了错误，所以我返回了错误字符串。如果状态码是 200，那么响应体就是一个 JSON 包装的对象，其包含翻译后的文本，因此我需要使用 `json.loads()` 函数来解析成 Python 对象。`content` 属性包含原始的响应体信息，但是字节对象，在传给 `json.loads()` 之前会转换成 UTF-8 字符串。

下面你可以在 Python 控制台中看到我是如何使用新的 `translate()` 函数的。

```shell
>>> from app.translate import translate
>>> translate('Hi, how are you today?', 'en', 'es')  # English to Spanish
'Hola, ¿cómo estás hoy?'
>>> translate('Hi, how are you today?', 'en', 'de')  # English to German
'Are Hallo, how you heute?'
>>> translate('Hi, how are you today?', 'en', 'it')  # English to Italian
'Ciao, come stai oggi?'
>>> translate('Hi, how are you today?', 'en', 'fr')  # English to French
"Salut, comment allez-vous aujourd'hui ?"
```

不错吧？现在是将这些功能整合到应用里了。

