# Section 1　Python 入门与初体验

> 本笔记由课程 PPT《Python 入门与初体验》整理转换，用于课堂讲解与课后复习。

---

### Introduction and Initial experience

- 入门与初体验
- Python、后端与数据库
- 第一章 Python 编程基础

### 初识 Python 与编程

- 1. 什么是编程语言
- 2. 编译型 vs 解释型
- 3. Python 的历史与由来
- 4. Python 2 还是 Python 3
- 5.  Python 能干什么
- 6. 为什么它这么火 / 好学
- 6. 代码是怎么跑起来的

### 什么是编程语言

- 编程 = 人给计算机下达指令
- 计算机只懂 0 和 1，人写不了，于是有了"编程语言"来翻译
- Python、Java、C……就像中文、英文，各有擅长的场景
- 一段指令叫「代码」，一个完成任务的文件叫「程序」
- 写代码，就是给一个记性超好、却完全不会变通的助理写便签。

### 编译型 vs 解释型

- 编译型（C / Go）：整本翻译成机器码，再运行 —— 快，但改动要重新编译
- 解释型（Python）：解释器一行行边翻译边执行 —— 写完即跑、改完即见效
- Python 属于「解释型」，所以需要一个「解释器」来运行
> 💡 编译 = 整本书翻译完再看；解释 = 请个同声传译，你说一句他译一句。


### Python 的历史与由来

- 1991 年，荷兰人 Guido van Rossum 发布 Python （曾供职于google，现任职于dropbox ）
- 名字来自英国喜剧团体 Monty Python，不是"蟒蛇"
- 免费使用和传播它，而不用担心版权的问题
- 设计哲学：Life is short, use Python（人生苦短）
- 追求"代码给人读"，所以语法特别接近自然英语
> 💡 一个程序员闲得慌造出来的语言，如今是全世界最流行的语言之一。

- 编程语言排行榜：TIOBE Index - TIOBE

### Python 2 还是 Python 3

- 只学 Python 3
- Python 有 2 和 3 两个版本，语法不完全兼容
- Python 2 已于 2020 年 1 月 正式停止维护
- 现在一律学、一律用 Python 3

### Python 能干什么

- Web 后端 —— 知乎、B 站、Instagram 的后台
- 数据分析 / 办公自动化 —— 上万行 Excel 一键汇总成报表
- AI / 大模型 —— ChatGPT 等几乎都用 Python
- 网络爬虫 —— 自动从网页抓数据存成表格
- 自动化脚本 /自动化运维 —— 定时改名、发邮件、出日报
- 常规软件开发 —— 比如建模软件 Blender ，Maya， 3dmax
- 科学计算 —— Matlab
- 云计算
- 大数据分析 —— 在大量数据的基础上，结合科学计算、机器学习等技术，对数据进行清洗、去重、规格化和针对性的分析是大数据行业的基石。Python是数据分析的主流语言之一。
- 做游戏（小游戏）

### 为什么它这么火 / 好学

- 1. 简单易学、明确优雅、开发速度快
- 简单易学：与C和Java比，Python的学习成本和难度曲线不是低一点，更适合新手入门，自底向上的技术攀爬路线。先订个小目标爬个小山，然后再往更高的山峰前进。而不像C和JAVA光语言学习本身，对于很多人来说就像珠穆朗玛峰一样高不可攀。
- 明确优雅：Python的语法非常简洁，代码量少，非常容易编写，代码的测试、重构、维护等都非常容易。一个小小的脚本，用C可能需要1000行，用JAVA可能几百行，但是用Python往往只需要几十行！
- 开发速度快：当前互联网企业的生命线是什么？产品开发速度！如果你的开发速度不够快，在你的产品推出之前别人家的产品已经上线了，你也就没有生存空间了，这里的真实例子数不胜数。那么，Python的开发速度说第二没人敢称第一!
- 2. 跨平台、可移植、可扩展、交互式、解释型、面向对象的动态语言
- 跨平台：Python支持Windows、Linux和MAC os等主流操作系统。
- 可移植：代码通常不需要多少改动就能移植到别的平台上使用。
- 可扩展：Python语言本身由C语言编写而成的，你完全可以在Python中嵌入C，从而提高代码的运行速度和效率。你也可以使用C语言重写Python的任何模块，从根本上改写Python，PyPy就是这么干的。
- 交互式：Python提供很好的人机交互界面，比如IDLE和IPython。可以从终端输入执行代码并获得结果，互动的测试和调试代码片断。
- 解释型：Python语言在执行过程中由解释器逐行分析，逐行运行并输出结果。
- 面向对象：Python语言具备所有的面向对象特性和功能，支持基于类的程序开发。
- 动态语言：在运行时可以改变其结构。例如新的函数、对象、甚至代码可以被引进，已有的函数可以被删除或是其他结构上的变化。动态语言非常具有活力。
- 3. 库 (理解为插件) 特别多，想干什么大概率有现成工具，pip 一键安装
- 4. 社区大且活跃、资料多，报错一搜就有答案
- 5. 数据、后端、AI 岗位需求高

### 代码是怎么跑起来的

- 你写的 hello.py 是纯文本，计算机直接看不懂
- Python 解释器读代码 → 一行行翻译执行 → 产出结果
- 没有解释器，代码就跑不起来
- hello.py ──► Python 解释器 ──► 屏幕打印 Hello World

### 小结（Python之禅）

- Beautiful is better than ugly.Explicit is better than implicit.Simple is better than complex.Complex is better than complicated.Flat is better than nested.Sparse is better than dense.Readability counts.Special cases aren't special enough to break the rules.Although practicality beats purity.Errors should never pass silently.Unless explicitly silenced.In the face of ambiguity, refuse the temptation to guess.There should be one-- and preferably only one --obvious way to do it.Although that way may not be obvious at first unless you're Dutch.Now is better than never.Although never is often better than *right* now.If the implementation is hard to explain, it's a bad idea.If the implementation is easy to explain, it may be a good idea.Namespaces are one honking great idea -- let's do more of those!
- 优美胜于丑陋（Python 以编写优美的代码为目标）明了胜于晦涩（优美的代码应当是明了的，命名规范，风格相似）简洁胜于复杂（优美的代码应当是简洁的，不要有复杂的内部实现）复杂胜于凌乱（如果复杂不可避免，那代码间也不能有难懂的关系，要保持接口简洁）扁平胜于嵌套（优美的代码应当是扁平的，不能有太多的嵌套）间隔胜于紧凑（优美的代码有适当的间隔，不要奢望一行代码解决问题）可读性很重要（优美的代码是可读的）即便假借特例的实用性之名，也不可违背这些规则（这些规则至高无上）不要包容所有错误，除非你确定需要这样做（精准地捕获异常，不写 except:pass 风格的代码）当存在多种可能，不要尝试去猜测而是尽量找一种，最好是唯一一种明显的解决方案
- （如果不确定，就用穷举法）虽然这并不容易，因为你不是 Python 之父
- 做也许好过不做，但不假思索就动手还不如不做（动手之前要细思量）如果你无法向人描述你的方案，那肯定不是一个好方案；反之亦然（方案测评标准）命名空间是一种绝妙的理念，我们应当多加利用（倡导与号召）

### 开发环境 PyCharm

- 1. 什么是 IDE
- 2. PyCharm vs VS Code
- 3. 安装 py 与 PyCharm
- 4. 新建第一个项目
- 5. 选择解释器
- 6.运行与调试

### 什么是 IDE

- 代码本质是文本，用记事本也能写，但很难写
- IDE = 集成开发环境，一个"全能工作台"
- 它帮你：语法高亮、自动补全、实时报错、一键运行、断点调试
- 我们用的 IDE 就是 PyCharm

### PyCharm vs VS Code

- 业界两大主流：PyCharm 与 VS Code
- PyCharm：为Python 而生，自动识别解释器、自动建虚拟环境、图形化装包 —— 新手少踩坑
- VS Code：更轻、更通用，什么语言都能写，但要自己装配置
- 本课统一用 PyCharm；

### 安装 Python 和 PyCharm

- Python Release Python 3.14.6 | Python.org
- PyCharm，您需要的唯一 Python IDE

### 新建第一个项目

- 认识 PyCharm 界面
- New Project → 选好项目位置，创建
- 左侧：项目文件区中间：代码编辑区
- 底部：终端（Terminal）　右上：运行按钮
- 右键 New → Python File，新建一个 .py 文件

### 运行与调试

- 点绿色三角，或右键 Run，代码就跑起来了
- 底部窗口能看到程序的输出结果
- 在行号左边点一下 =  打「断点」
- Debug 模式下程序会停在断点，一步步看它怎么走—— 排错神器
