The Flask Mega-Tutorial Part XV: A Better Application Structure
===

原文地址: [The Flask Mega-Tutorial Part XV: A Better Application Structure](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure)

这是 Flask Mega-Tutorial 系列的第十五篇文章了，在这里我将使用一种适合更大型应用的风格来重构应用。

目前博客应用的大小适中，所以我考虑现在是讨论 Flask 应用如何增长但是不会导致太混乱以致无法管理的好时候。Flask 是一个提供给你以任意方式组织项目的框架，而且作为它的设计哲学，它也使得当应用变大的时候改变或者调整应用结构成为可能，或者当你的需求，经验层级改变的时候。

在本章我将讨论一些应用于大型应用的一些模式，为了说明它们我将对我的博客项目的结构做一些改变，让代码变得更加可维护并且组织良好。当然，以真正的 Flask 精神，我鼓励你在组织你自己的项目的时候将这些改变作为一个建议。

本章的 Github 链接为：[Browse](https://github.com/miguelgrinberg/microblog/tree/v0.15), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.15.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.14...v0.15)
