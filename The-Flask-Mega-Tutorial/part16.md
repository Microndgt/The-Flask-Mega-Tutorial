The Flask Mega-Tutorial Part XVI: Full-Text Search
===

原文地址: [The Flask Mega-Tutorial Part XVI: Full-Text Search](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search)

这是 Flask Mega-Tutorial 系列的第十六篇文章，在这里我将向微博应用中添加全文搜索功能。

本章的目标是向微博应用中实现搜索功能，这样用户就可以使用自然语言来找到感兴趣的博文。对于很多类型的 web 站点，只使用谷歌，必应等来索引所有的内容并且通过它们的搜索 API 来提供搜索内容。这对于只有静态页面的站点比如论坛，可以很好的工作。但是在我的应用中，内容的基础组件是一个用户的微博，只是整个页面中的一小部分。我需要的搜索结果是这些单独的微博而不是整个页面。比如，我想在这些单独的微博中搜索 `dog`，只要微博中包含这个关键词即可。当然一个展示所有微博的页面会包含这个关键字，但是强大的搜索引擎可以找到微博的位置，因此我需要实现我自己的搜索引擎。

本章的 Github 链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.16), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.16.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.15...v0.16)

全文搜索引擎的介绍
===

全文搜索没有被比如关系型数据库标准化。有几个开源的全文搜索引擎：Elasticsearch, Apache Solr, Whoosh, Xapian, Sphinx 等等。而且仍有一些数据库支持如上面提到的搜索引擎支持搜索功能。SQLite, MySQL 和 PostgreSQL 都支持文本搜索，NoSOL 数据库比如 MongoDB 和 CouchDB 也同样支持。

如果你疑问上面哪些可以在 Flask 应用中工作，答案是都可以！这就是 Flask 强大之处，它不会被武断的决定使用什么数据库。那么哪个是最好的选择呢？

在上面专注做搜索引擎中的，Elasticsearch 对于我来说是比较突出的一个，而且比较流行，部分原因是因为它是 ELK stack(ELK stack是以Elasticsearch、Logstash、Kibana三个开源软件为主的数据处理工具链，是目前开源界最流行的实时数据分析解决方案，成为实时日志处理领域开源界的第一选择。) 中的 E，用来索引日志。使用关系型数据库的文本搜索能力也是一个好的选择，但是 SQLAlchemy 不支持这样的功能，所以我得自己写原生的 SQL 语句，或者是找到一个提供文本搜索的高层次使用的包，并且能和 SQLAlchemy 共存。

基于上面的分析，我将会使用 Elasticsearch，但是我将使用一种可以容易切换成其他引擎的实现文本索引和搜索的方式。这将允许你仅仅需要修改一个模块中的几个函数就可以切换另一个搜索引擎。

安装 ElasticSearch
===

有好几种方式安装 ElasticSearch，比如安装包，需要自己安装的 zip 源码包，甚至是一个 Docker 镜像。文档对于这几张方式有详细的安装介绍。如果你使用 Linux，对于你的版本可能会有一个可用的包。如果使用 Mac 并且已经安装了 Homebrew，你可以简单的运行 `brew install elasticsearch`

一旦你安装了 Elasticsearch，你可以通过访问 `http://localhost:9200` 来确保安装成功，它应该以 JSON 格式返回一些关于服务的基本信息。

因为我会通过 Python 来使用 Elasticsearch，所以我会安装一个 Python 客户端：

```shell
(venv) $ pip install elasticsearch
```

并且更新 requirements.txt 文件：

```shell
(venv) $ pip freeze > requirements.txt
```

ElasticSearch 指南
===

