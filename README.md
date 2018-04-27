# 《The Flask Mega-Tutorial》翻译计划

进度 ![](https://img.shields.io/badge/status-52%25-green.svg)

- 原文地址: [blog.miguelgrinberg.com](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- 作者: `miguelgrinberg`

简介
---

`The Flask Mega-Tutorial` 主要以 Flask 为 Web 框架，数据库使用关系型数据库，`Flask-SQLAlchemy` 为 ORM，`Flask-Migrate` 做数据库迁移工具，通过完成一个博客网站遇到的种种问题作为主线，提出相应的解决方法，从而完成整个网站的设计和搭建。

通过阅读本文，你可以了解到在设计一个网站时候需要考虑什么，会遇到什么问题，可能的解决方式是什么，由此你可以对 Web 设计和开发有一个更全面的把握。

注: 

1. 翻译内容可能不会和原文完全一样，这里对一些比较啰嗦的语句做了删节，但是会保证原意一致。
2. 在翻译的同时，译者会添加一些相关实践中用到的东西以供参考。相关内容后都会有 `[译者注]` 标记。

参与
---

Fork 本仓库，翻译原文一部分，然后向本仓库提交一个 PR。可以是新的翻译，也可以是提 issue 以及任何有助于本项目的提交。

- PR 以一篇文章为单位。
- 在准备翻译某篇文章之后，请先看一下目前 master 分支的翻译进度和打开的PR，避免多个人翻译同一个地方。如果暂时还没有翻译，那么迅速初始化并且完成初始提交，并且开一个 PR。
- 如果仍然出现多人发了同一节的 PR，那么将会按照时间顺序接受第一个 PR，后面的会拒绝 PR。
- 一旦提交了 PR，那么请尽快的翻译，与此同时项目组也会对翻译内容进行 review，还请翻译者不断的润色和优化。
- 内容使用 Markdown 组织。

格式说明
---

1. 代码块部分请注明语言，在 Github 上可以对不同语言的代码进行渲染，方便阅读。参见 `issue#4`
2. 字母，数字等字符和中文字符之间留有空格，方便阅读。中文正则匹配表达式 `[\u4e00-\u9fa5]`。参见 `issue#4`
3. 其他格式排版参考 `master` 中已经翻译的部分。

目录
---

- [Part I: Hello, World!](https://github.com/Microndgt/The-Flask-Mega-Tutorial/blob/master/The-Flask-Mega-Tutorial/part1.md) - done - 100%
- [Part II: Templates](https://github.com/Microndgt/The-Flask-Mega-Tutorial/blob/master/The-Flask-Mega-Tutorial/part2.md) - done - 100%
- [Part III: Web Forms](https://github.com/Microndgt/The-Flask-Mega-Tutorial/blob/master/The-Flask-Mega-Tutorial/part3.md) - done - 100%
- [Part V: User Logins](https://github.com/Microndgt/The-Flask-Mega-Tutorial/blob/master/The-Flask-Mega-Tutorial/part5.md) - done - 100%
- [Part VII: Error Handling](https://github.com/Microndgt/The-Flask-Mega-Tutorial/blob/master/The-Flask-Mega-Tutorial/part7.md) - done - 100%
- [Part VIII: Followers](https://github.com/Microndgt/The-Flask-Mega-Tutorial/blob/master/The-Flask-Mega-Tutorial/part8.md) - done - 100%
- [Part IX: Pagination](https://github.com/Microndgt/The-Flask-Mega-Tutorial/blob/master/The-Flask-Mega-Tutorial/part9.md) - done - 100%
- [Part XII: Dates and Times](https://github.com/Microndgt/The-Flask-Mega-Tutorial/blob/master/The-Flask-Mega-Tutorial/part12.md) - done - 100%
- [Part XIX: Ajax](https://github.com/Microndgt/The-Flask-Mega-Tutorial/blob/master/The-Flask-Mega-Tutorial/part14.md) - done - 100%
- [Part XV: A Better Application Structure](https://github.com/Microndgt/The-Flask-Mega-Tutorial/blob/master/The-Flask-Mega-Tutorial/part15.md) - done - 100%

贡献者
===

Pull Request
---

- [Microndgt](https://github.com/Microndgt)
- [vsxen](https://github.com/vsxen)
- [zenghongtu](https://github.com/zenghongtu)

Issue
---

- [lanpong](https://github.com/lanpong)

工具
===

issue#4 文档格式检查工具
---

使用了 [fire](https://github.com/google/python-fire)

- 查看帮助：`python format.py -- --help`

```
Type:        function
String form: <function fix_format at 0x10ed82048>
File:        format.py
Line:        35

Usage:       format.py PATH [VERBOSE] [TEST]
             format.py --path PATH [--verbose VERBOSE] [--test TEST]
             --test 只进行测试，并不输出文件
             --verbose 显示格式检查详情
```

`python format.py README.md  --test --verbose`
