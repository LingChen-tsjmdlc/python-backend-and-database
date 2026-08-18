# 作业系统搭建步骤（PLAN）

> 目标：用 YAML 存题、PySide + HeroSideUI 做界面，搭建课程作业工具。
> 主任务：布置作业（单选 + 填空 + 代码分析 + 代码解析 + 写代码实践，题量分值每份卷子自定）。
> 顺带目标：在真实需求下验证 HeroSideUI 组件库。
> 原则：判分逻辑与界面彻底解耦，题目内容与代码彻底解耦。

---

## 一、已拍板的决策

| # | 决策点 | 结论 |
|---|--------|------|
| D1 | 项目放哪 | 本仓库 `homework/` 下 |
| D2 | 答案存哪 | 与题目同文件（自测工具，提交后才展示） |
| D3 | HeroSideUI 引用 | TestPyPI：`herosideui==0.8.0`（⚠️ 不能用 pip 的 `-i` 直接装，见 P0） |
| D4 | 编程题判分 | 手动批改；自动批改（跑测试用例）列 v2 |

---

## 二、总体架构（三层，单向依赖）

```
assignments/*.yaml          题库（数据）
        │
        ▼
core/                       加载 + 校验 + 解析 + 判分（纯 Python，无 Qt 依赖，可单独 pytest）
        │
        ▼
app/                        PySide + HeroSideUI（只管显示与收集答案）
```

铁律：
1. **UI 不算分**。分数只来自 `core.grade()`，单一事实来源。
2. **core 不 import Qt**。将来换 Web 界面、命令行批改都不动 core。
3. **新题型 = 注册一个 renderer + 一个 grader**，core 和主窗口零改动。
4. **学员代码只解析、不执行**。`ast.parse` 是安全上限，执行判分进 v2 沙箱方案。

---

## 三、YAML Schema（v1）

### 关键设计决定

- **"代码分析题"不是独立题型**——它是"带 `code` 字段的单选题"。任何题型都可以挂代码上下文。
- v1 实现 4 种题型键：`single_choice` / `fill_blank` / `code_explain` / `programming`。
  - 代码分析题 = `single_choice` + `code`
  - 代码解析题 = `code_explain`（自由文本，手动批改）
  - 写代码实践 = `programming`（作答方式：传入 .py 文件）
- `multi_choice`（多选）schema 预留，实现列 v1.5。
- `programming` 的 `grading` 字段预留 `self / manual / tests`，v1 只实现 `manual`（AST 解析辅助 + 人工批改）。

### 通用字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | str | 是 | 文件内唯一，如 `sc-01` |
| `type` | str | 是 | `single_choice` / `fill_blank` / `code_explain` / `programming` |
| `points` | int | 是 | 分值 |
| `stem` | str | 是 | 题干 |
| `code` | str | 否 | 代码上下文（字面量块 `|`） |
| `explanation` | str | 否 | 解析，提交后展示 |
| `tags` | list | 否 | 预留分类/筛选 |

### 文件头

```yaml
version: 1
id: part1-section2
title: 第 2 节 · 变量与数据类型
questions: [ ... ]
```

### 题型 1：single_choice（含代码分析题）

```yaml
- id: sc-01
  type: single_choice
  points: 4
  stem: 下列哪个是合法的 Python 变量名？
  options:
    - { key: A, text: "2nd_place" }
    - { key: B, text: "player-score" }
    - { key: C, text: "player_score" }
    - { key: D, text: "class" }
  answer: C
  explanation: 标识符不能以数字开头、不能含连字符、class 是关键字。

# 代码分析题 = 单选 + code 字段
- id: ca-01
  type: single_choice
  points: 6
  code: |
    a = [1, 2, 3]
    b = a
    b.append(4)
    print(a)
  stem: 上述代码的输出是？
  options:
    - { key: A, text: "[1, 2, 3]" }
    - { key: B, text: "[1, 2, 3, 4]" }
    - { key: C, text: "抛出异常" }
  answer: B
  explanation: b = a 是引用赋值，两个名字指向同一个列表。
```

### 题型 2：fill_blank（支持多空）

```yaml
- id: fb-01
  type: fill_blank
  points: 3
  stem: "表达式 len(\"hello\") 的值是 ____，type(1 + 1.0) 是 ____。"
  blanks:
    - answer: "5"
    - answer: float
      accept: ["<class 'float'>", "float()"]   # 可选，任一命中即对
  explanation: len 返回字符数；int 与 float 运算结果是 float。
```

判分规则：每空先 `strip()` 再字符串比对；`accept` 列表任一命中即对；多空均分题目分值。大小写敏感（v1 固定，字段 `case_insensitive` 留给 v1.5）。

### 题型 3：code_explain（代码解析题，手动批改）

```yaml
- id: ce-01
  type: code_explain
  points: 8
  code: |
    total = 0
    for i in range(10):
        total = total + i
    print(total / 10)
  stem: 解释这段代码的作用，并指出可能的问题或可改进之处。
  rubric:                # 批改参考要点，结果页对照打分
    - 说出"计算 0~9 的平均值并打印"
    - 指出变量命名（i/total）语义不清
    - 指出除法结果是 4.5（真除法）而非 4
  reference: |           # 示范回答，提交后展示
    这段代码把 0 到 9 累加后除以 10，打印平均值 4.5。
    问题：变量命名不够语义化；魔数 10 重复出现且含义不同。
  explanation: 真除法 / 在 Python 3 返回 float。
```

作答：自由文本（Textarea）。判分：**手动**——提交后展示 rubric 要点 + 示范回答，批改人在结果页按要点给分，报告标记 `manual_graded`。

### 题型 4：programming（写代码实践，传入 py 文件）

```yaml
- id: pg-01
  type: programming
  points: 15
  stem: 编写函数 bmi(weight_kg, height_m)，返回 BMI 值，保留一位小数。
  starter: |                # 起始代码，可复制到自己的编辑器
    def bmi(weight_kg: float, height_m: float) -> float:
        ...
  reference: |              # 参考答案，提交后展示
    def bmi(weight_kg: float, height_m: float) -> float:
        return round(weight_kg / height_m ** 2, 1)
  expect_defs: [bmi]        # 可选，AST 检查必须出现的函数/类名
  checklist:                # 人工批改自查清单
    - 函数名与参数签名正确
    - 使用幂运算而不是重复乘法
    - 结果保留一位小数
  grading: manual           # manual（v1）| self | tests（v2）
```

作答：**选择本地 .py 文件**（Button + QFileDialog）。提交后系统对文件做"解析"：
1. `ast.parse()` 语法校验（不执行任何代码）
2. 提取定义清单（函数名、参数、类）——`expect_defs` 缺失即标黄提示
3. 结果页展示解析结果 + 参考答案 + checklist，批改人给分

文件管理：提交时把所选文件复制到 `submissions/<assignment_id>/<qid>/answer.py`，报告与文件对应。

### 判分规则汇总

| 题型 | 判分方式 | 规则 |
|------|----------|------|
| single_choice | 自动 | 所选 == answer 得满分，否则 0 |
| fill_blank | 自动 | 逐空 strip 比对 / accept 命中；多空均分 |
| code_explain | 手动 | rubric 要点 + reference 对照，结果页给分，标 `manual_graded` |
| programming | 解析辅助 + 手动 | ast.parse 校验语法、提取定义、核对 expect_defs；人工按 checklist 给分 |

`grade()` 返回的报告分两部分：
- **auto**：自动题得分（单选 + 填空），提交即出
- **manual**：待人工题（代码解析 + 编程），逐题给分后并入总分；未给分时界面显示"自动 X 分 / 满分 Y，另有 Z 分待批改"

未作答（选项没选 / 文本为空 / 没选文件）一律计 0 并标记 `unanswered`。

### 分值示例（仅示例，每卷自定）

单选 4×6=24，填空 3×4=12，代码分析 6×3=18，代码解析 8×2=16，编程 15×2=30 → 总分 100。loader 校验 `sum(points)`，不为 100 时 warning（不阻断）。

---

## 四、core 层接口（纯函数）

```python
# core/schema.py —— pydantic 模型，yaml 进来先过校验
Question = SingleChoice | FillBlank | CodeExplain | Programming
Assignment = {version, id, title, questions: list[Question]}

# core/loader.py
load_assignment(path: Path) -> Assignment          # 读 yaml + pydantic 校验 + id 查重
discover_assignments(dir: Path) -> list[Assignment] # 扫描 assignments/*.yaml

# core/parse.py —— 学员 py 文件解析（只读不执行）
parse_py_file(path: Path, expect_defs: list[str] | None) -> ParseResult
# ParseResult = {ok, syntax_error, defs: [{name, kind, params}]}

# core/grader.py
grade(assignment, answers: dict[qid, Answer]) -> GradeReport
# Answer 形如：
#   {"sc-01": {"selected": "C"}}
#   {"fb-01": {"values": ["5", "float"]}}
#   {"ce-01": {"text": "这段代码..."}}
#   {"pg-01": {"file": "E:/.../answer.py"}}
# GradeReport = {auto: {earned, total},
#                manual: {earned, total, items: [...]},
#                items: [{qid, type, verdict, earned, parse_result?, detail}]}
# verdict ∈ correct | wrong | partial | pending_manual | unanswered
```

---

## 五、目录结构

```
homework/
├── PLAN.md                # 本文档
├── assignments/           # 题库，每章一个 yaml
│   └── part1_section2.yaml
├── submissions/           # 提交的 py 文件归档（按 assignment/qid）
├── core/                  # 纯逻辑层（无 Qt）
│   ├── schema.py
│   ├── loader.py
│   ├── parse.py           # AST 解析，不执行代码
│   └── grader.py
├── app/                   # 界面层
│   ├── main.py
│   ├── window.py          # 主窗口 + 页面流转
│   └── renderers/         # 每题型一个渲染器
│       ├── single_choice.py
│       ├── fill_blank.py
│       ├── code_explain.py
│       └── programming.py
└── tests/                 # core 层测试（不依赖 GUI）
    ├── test_loader.py
    ├── test_parse.py
    └── test_grader.py
```

## 六、组件映射（HeroSideUI 用在哪）

| 界面元素 | 组件 | 说明 |
|----------|------|------|
| 章节/作业列表 | Listbox | 数据来自 discover_assignments() |
| 题卡容器 | Card | 每题一张，含题号与分值 |
| 单选选项 | Radio | |
| 填空作答 | Input | 多空则多个 Input，与题干 ____ 对应 |
| 代码解析作答 | Textarea | 自由文本 |
| 编程题选文件 | Button + QFileDialog | 选定后 Chip 显示文件名，可移除重选 |
| 代码上下文/参考答案 | CodeBlock | 代码分析/解析题、编程题 starter/reference |
| 提交 | Button | |
| 作答进度 | Progress | 已答/总题数 |
| 判分结果 | Alert | 自动部分即时出：优秀 success / 及格 warning / 低分 danger |
| 待批改区 | Card + Input | 手动题逐题给分入口 |
| 解析展开 | Accordion | 提交后才渲染，默认收起 |
| 读取题库占位 | Skeleton | yaml 加载期间 |
| 主题切换 | ThemeSwitcher | 全局亮暗 |

---

## 七、实施步骤（每阶段有验收，过了才进下一阶段）

### P0 决策与环境
决策已定（见第一节）。搭环境（**命令自己执行**）：

```bash
cd E:/git-clone-projects/python-backend-and-database/homework
uv init --name homework-studio
```

然后在 `pyproject.toml` 里把 TestPyPI 配成**附加索引**（不能用它替换默认源，PySide6 等依赖只在官方 PyPI 有）：

```toml
[[tool.uv.index]]
url = "https://test.pypi.org/simple/"
```

再装依赖：

```bash
uv add "herosideui[pyside6]==0.8.0" pyyaml pydantic
uv add --dev pytest pytest-qt
```

> ⚠️ 之所以不直接 `pip install -i https://test.pypi.org/simple/ herosideui==0.8.0`：pip 的 `-i` 会**整体替换**索引源，TestPyPI 上没有 PySide6/pydantic 等依赖，装到一半必报 "No matching distribution"。uv 的附加索引模式下依赖自动回落官方源，没这个问题。
> TestPyPI 版本与正式 PyPI 不同步，版本号务必钉死（==0.8.0），升级时改这一处。

验收：`uv run python -c "from hero_side_ui import Button; print('ok')"` 输出 ok。

### P1 core 层（先于一切界面代码）
产出：`schema.py` / `loader.py` / `parse.py` / `grader.py` + `tests/`。
测试要点：
- schema 拒绝坏数据（缺 answer、id 重复、未知 type、code_explain 无 rubric）
- 判分覆盖：全对/全错/部分对（多空）、accept 命中、strip 生效、未作答计 0
- parse：合法文件提取 defs、语法错误返回 syntax_error、expect_defs 缺失标黄、文件不存在
- manual 题：未给分时 verdict=pending_manual 且不计入 auto；给分后并入

验收：`uv run pytest` 全绿；用 fixture 题库跑 grade() 得到手工核算的分数。

### P2 第一份题库
`assignments/part1_section2.yaml`，覆盖全部 4 种题型（含代码分析变体）。
验收：loader 校验通过、无 warning、id 无重复。

### P3 UI 骨架
主窗口 + 左侧章节 Listbox + 右侧题目滚动区 + 底部提交栏。题目先用占位 Card。
验收：跑起来能加载 yaml 并显示占位卡；进度条随作答更新。

### P4 题型渲染器
4 个 renderer + 注册表 `RENDERERS: dict[type, Callable]`。渲染器职责：把 Question 变成 QWidget，并能吐出 Answer（含编程题的文件选择与复制时机）。
验收：逐题作答后能收集到完整 `dict[qid, Answer]`，形状与 core 约定一致。

### P5 判分闭环
提交 → `core.grade()` → 结果页：
- 自动题：总分 Alert + 逐题正误 + Accordion 解析
- 手动题：AST 解析结果 + rubric/reference/checklist 对照 + 给分输入，给分即更新总分（标 `manual_graded`）

验收：故意答错若干题，自动分 == pytest fixture 计算的分数；编程题选一个语法错误的文件，界面正确标红并显示 syntax_error。

### P6 打磨与组件验证记录
- ThemeSwitcher 全局切换，已作答状态不丢
- Skeleton 加载态、判分中 Spinner（可选）
- **组件观察点**（这是验证组件库的正题）：
  - 全量 Card 数据驱动重建的性能
  - 切主题时已渲染组件（Radio/Input/Textarea 已选/已填状态）是否保持
  - CodeBlock 长行、中文、横向滚动表现
  - Input 多空场景的焦点流转（Tab 顺序）
  - Textarea 长文本（代码解析答案）滚动与光标
  - Listbox 章节数量增长后的滚动
- 发现的问题逐条记入 HeroSideUI 仓库 backlog（含复现最小示例）

验收：亮暗两主题各截一张全卷截图；组件问题清单（可为空）。

---

## 八、风险与已知的坑

| 风险 | 对策 |
|------|------|
| TestPyPI 依赖缺失（-i 替换源的经典坑） | 用 uv 附加索引，见 P0 |
| 环境混用：全局 python313 挂着 PIP_TARGET 自定义目录 | 本项目一律走 uv 独立 venv，不用全局解释器跑 app |
| yaml 里写代码块缩进错（Python 代码对缩进敏感） | 代码一律用 `|` 字面量块；loader 校验后打印预览人工抽查 |
| 学员 py 文件是外部输入 | 只 ast.parse 不执行；文件复制归档；不信任任何路径，只接受 .py 后缀 |
| 答案与题目同仓公开 | v1 是自测工具可接受；将来计分场景把 assignments/ 移私有仓，接口不变 |
| 判分口径不一致 | 界面永不自行算分，只调 core.grade()；手动给分也写回 GradeReport |

## 九、v2 方向（明确不进 v1）

- 编程题 `grading: tests`：沙箱子进程跑 pytest 判分（执行学员代码前必须做隔离）
- 简易内置代码编辑器（替换"外部写好传文件"）
- `multi_choice` 多选题（schema 已预留形态）
- 随机抽题 / 选项乱序（seed 可复现）
- 错题重练模式、成绩导出 CSV、计时
