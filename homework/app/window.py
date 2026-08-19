"""app.window —— 主窗口（v2 布局）。

启动页（两 Card 选模式）→ 姓名页 → 作业页（左侧题库 + 右侧题型 Tabs）。
中：垂直 Divider 分割
右：标题 + 题型 Tabs + 底部整卷提交按钮
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from hero_side_ui import (
    Alert,
    Button,
    Card,
    CardBody,
    Divider,
    Input,
    Subtitle,
    Tabs,
    Text,
    ThemeProvider,
    ThemeSwitcher,
    Title,
)

from core.answers import load_answers, save_answers, student_answers_path, submit_answers
from core.loader import load_assignment
from core.schema import (
    Answer,
    Assignment,
    GradeReport,
    ProgrammingAnswer,
)

from .renderers import create_renderer
from .renderers.base import QuestionRenderer

from .paths import BANK_ROOT, PART_LABELS

# 四个题型 Tab（顺序即展示顺序）；single_choice 含"代码分析"变体
TYPE_TABS = [
    ("single_choice", "单选 · 代码分析"),
    ("fill_blank", "填空"),
    ("code_explain", "代码解析"),
    ("programming", "编程"),
]


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("作业 · homework-studio")
        self.resize(1280, 840)

        self._theme_provider = ThemeProvider.instance()

        self._assignments: dict[str, Assignment] = {}   # aid -> assignment
        self._bank_paths: dict[str, Path] = {}          # aid -> 题库文件路径
        self._assignment: Assignment | None = None
        self._renderers: dict[str, QuestionRenderer] = {}
        self._reviews: dict = {}                      # 老师批改记录
        self._cards: dict = {}                         # qid -> 题卡（Alert 插入用）
        self._report: GradeReport | None = None
        self._student_name: str = ""
        self._answers_file: Path | None = None
        self._saved_status: str = ""
        self._dirty: bool = False

        # 防抖保存定时器：内容停稳 500ms 后写盘
        from PySide6.QtCore import QTimer
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self._flush_save)

        # 编程题轮询（CodeEditor 信号风暴规避）：2s 比对内容
        self._poll_editors: list = []
        self._editor_snapshot: dict[int, object] = {}
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(2000)
        self._poll_timer.timeout.connect(self._poll_programming)

        # 页面容器：启动页 / 姓名页 / 作业页，堆叠切换
        self._stack = QStackedWidget()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._stack)

        from .grade_page import GradePage
        self._build_start_page()
        self._build_name_page()
        self._build_work_page()
        self._grade_page = GradePage(self._stack, self._theme_provider)
        self._stack.addWidget(self._grade_page)     # 页 3：批改

        self._build_theme_switcher()            # 浮动控件，最后建、永远置顶

    # ------------------------------------------------------------------
    # 页 1：启动页（两张大 Card 选模式）
    # ------------------------------------------------------------------

    def _build_start_page(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(48, 48, 48, 48)

        do_card = self._mode_card("✍️", "写作业", "选择章节，开始作答与提交")
        do_card.pressed.connect(lambda: self._stack.setCurrentIndex(1))   # 官方 pressed 信号

        grade_card = self._mode_card("📝", "批改", "批改学生提交的作业")
        grade_card.pressed.connect(self._enter_grade_page)

        cards = QHBoxLayout()
        cards.setSpacing(24)
        cards.addWidget(do_card)
        cards.addWidget(grade_card)

        cards_host = QWidget()
        cards_host.setLayout(cards)
        cards_host.setSizePolicy(                        # 收缩到内容，垂直水平都不扩张
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum,
        )

        lay.addStretch(1)
        lay.addWidget(cards_host, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addStretch(1)

        self._stack.addWidget(page)

    def _mode_card(self, icon: str, title: str, desc: str) -> Card:
        card = Card(is_pressable=True)
        card.setFixedWidth(320)                          # 固定卡片宽，居中观感稳定
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Maximum)
        body = CardBody()
        bl = body.layout()
        bl.setContentsMargins(28, 28, 28, 28)
        bl.setSpacing(10)
        for t in (Text(icon, size="5xl"), Text(title, size="2xl", weight="bold")):
            t.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)   # 穿透，点击全部归 Card
            bl.addWidget(t)
        d = Text(desc)
        d.setWordWrap(True)
        d.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        bl.addWidget(d)
        card.add_body(body)
        return card

    # ------------------------------------------------------------------
    # 页 2：姓名页
    # ------------------------------------------------------------------

    def _build_name_page(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(48, 48, 48, 48)
        lay.setSpacing(16)

        back = Button("← 返回")
        back.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        lay.addWidget(back, alignment=Qt.AlignmentFlag.AlignLeft)

        lay.addStretch(2)
        lay.addWidget(Title("你的名字", level=2))
        self._name_input = Input(placeholder="请输入姓名")
        self._name_input.setFixedWidth(360)
        self._name_input.returned.connect(self._confirm_name)
        lay.addWidget(self._name_input, alignment=Qt.AlignmentFlag.AlignLeft)

        self._name_err = Text("", color="danger")
        lay.addWidget(self._name_err, alignment=Qt.AlignmentFlag.AlignLeft)

        next_btn = Button("下一步")
        next_btn.clicked.connect(self._confirm_name)
        lay.addWidget(next_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        lay.addStretch(3)

        self._stack.addWidget(page)

    def _enter_grade_page(self) -> None:
        self._grade_page.refresh()
        self._stack.setCurrentIndex(3)

    def _confirm_name(self) -> None:
        name = self._name_input.text().strip()
        if not name:
            self._name_err.setText("姓名不能为空")
            return
        self._name_err.setText("")
        self._student_name = name

        # 姓名就位 → 挂载作业（首次进入，或返回后换名重挂）
        if self._assignment is not None:
            self._on_assignment_picked(self._assignment.id)
        else:
            first = next(iter(self._assignments), None)
            if first:
                self._on_assignment_picked(first)
        self._stack.setCurrentIndex(2)

    # ------------------------------------------------------------------
    # 页 3：作业页（原主界面）
    # ------------------------------------------------------------------

    def _build_work_page(self) -> None:
        page = QWidget()
        root = QHBoxLayout(page)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(16)

        top = QVBoxLayout()
        top.setSpacing(8)
        top.addWidget(Title("课程作业", level=3))
        top.addWidget(self._build_back_button())
        top.addWidget(self._build_bank_list(), stretch=1)   # 题库滚动列表

        side = QWidget()
        side.setLayout(top)
        side.setFixedWidth(260)
        root.addWidget(side, stretch=0)

        root.addWidget(Divider(orientation="vertical"))

        right = QVBoxLayout()
        right.setSpacing(10)
        right.addWidget(self._build_header(), stretch=0)
        right.addWidget(self._build_tabs(), stretch=1)
        right.addWidget(self._build_footer(), stretch=0)
        wrap = QWidget()
        wrap.setLayout(right)
        root.addWidget(wrap, stretch=1)

        self._stack.addWidget(page)
        self._load_bank()

    def _build_back_button(self) -> QWidget:
        """作业页返回：回姓名页。"""
        back = Button("← 返回")
        back.clicked.connect(lambda: self._stack.setCurrentIndex(1))
        return back

    # ---------------- left（作业页侧栏内容，挂进 _build_work_page 的 top 布局） ----------------

    def _build_bank_list(self) -> None:
        """题库平铺列表：部分标题 + 分割线 + 作业按钮（填充在 _work_page 构建后）。"""
        self._bank_host = QWidget()               # 平铺：部分标题 + 作业按钮
        self._bank_lay = QVBoxLayout(self._bank_host)
        self._bank_lay.setContentsMargins(0, 0, 0, 0)
        self._bank_lay.setSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(self._bank_host)
        return scroll

    def _build_theme_switcher(self) -> None:
        """主题切换按钮：浮动钉在窗口左下角（Web fixed 效果）。"""
        self._theme_btn = ThemeSwitcher(parent=self)   # 主窗口直接作父，脱离布局
        self._theme_btn.raise_()                        # 浮在其他控件之上
        self._reposition_theme_btn()

    def _reposition_theme_btn(self) -> None:
        if not hasattr(self, "_theme_btn"):
            return
        m = 16                                           # 距左、下的边距
        self._theme_btn.move(m, self.height() - self._theme_btn.height() - m)

    def resizeEvent(self, event) -> None:               # 窗口缩放时保持钉在左下
        super().resizeEvent(event)
        self._reposition_theme_btn()

    # ---------------- right ----------------

    def _build_header(self) -> QWidget:
        row = QHBoxLayout()
        self._title = Title("选择左侧的作业开始", level=1)
        row.addWidget(self._title, stretch=1)
        w = QWidget()
        w.setLayout(row)
        return w

    def _build_tabs(self) -> QWidget:
        self._tabs = Tabs()                      # 默认变体，不指定 color
        self._tabs_host = QWidget()
        self._tabs_lay = QVBoxLayout(self._tabs_host)
        self._tabs_lay.setContentsMargins(0, 0, 0, 0)
        self._tabs_lay.addWidget(self._tabs)
        return self._tabs_host

    def _build_footer(self) -> QWidget:
        self._submit_btn = Button(
            "提交全部题目", full_width=True,      # 撑满右边宽度；其余默认样式
        )
        self._submit_btn.clicked.connect(self._on_submit)
        return self._submit_btn

    # ------------------------------------------------------------------
    # 题库加载（平铺：部分标题 + 作业按钮）
    # ------------------------------------------------------------------

    def _load_bank(self) -> None:
        for part_idx, (part_dir, part_label) in enumerate(PART_LABELS.items()):
            banks = sorted((BANK_ROOT / part_dir).glob("section*.yaml"))

            if part_idx > 0:                      # 部分之间用水平分割线隔开
                self._bank_lay.addSpacing(4)
                sep = Divider()
                # 竖直布局内：水平铺满、垂直锁死 1px，避免被拉高撑出滚动
                sep.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
                )
                self._bank_lay.addWidget(sep)
                self._bank_lay.addSpacing(4)

            label = Text(part_label, size="lg")
            label.setWordWrap(True)               # 长标题换行，不撑横向滚动
            self._bank_lay.addWidget(label)

            for p in banks:
                res = load_assignment(p)
                a = res.assignment
                self._assignments[a.id] = a
                self._bank_paths[a.id] = p
                btn = Button(
                    f"{a.title}",
                    color="primary", variant="flat", size="sm",
                    full_width=True,
                )
                btn.clicked.connect(
                    lambda _=False, aid=a.id: self._on_assignment_picked(aid)
                )
                self._bank_lay.addWidget(btn)

        self._bank_lay.addStretch(1)

        # 默认选第一份
        first = next(iter(self._assignments), None)
        if first and self._student_name:          # 有姓名才自动选中并挂载答案文件
            self._on_assignment_picked(first)

    # ------------------------------------------------------------------
    # 选中作业 → 渲染题型 Tabs → 恢复已存答案
    # ------------------------------------------------------------------

    def _on_assignment_picked(self, aid: str) -> None:
        self._assignment = self._assignments.get(aid)
        if self._assignment is None:
            return

        # 学生答案文件：题库同级 / <姓名> / <同名>.yaml
        bank_yaml = self._bank_paths[aid]
        self._answers_file = student_answers_path(bank_yaml, self._student_name)
        saved, status, report, reviews = load_answers(self._answers_file, self._assignment)
        self._saved_status = status
        self._report = report
        self._reviews = reviews

        self._render_tabs()
        self._restore_answers(saved)
        self._submit_btn.setEnabled(not (status == "submitted"))   # 已提交：锁定
        self._show_status_in_title()

        # 已提交：作答区锁定 + 每题顶部 Alert 显示判分/批改结果
        if status == "submitted":
            for r in self._renderers.values():
                r.set_disabled(True)
            self._show_review_alerts()

        # 编程题轮询启停 + 初始快照
        self._poll_timer.stop()
        if self._poll_editors and status != "submitted":
            self._editor_snapshot = {id(r): r.collect() for r in self._poll_editors}
            self._poll_timer.start()

    def _restore_answers(self, saved: dict[str, Answer]) -> None:
        """把存盘答案灌回渲染器（渲染器各带 restore 方法）。"""
        for qid, ans in saved.items():
            r = self._renderers.get(qid)
            if r is None:
                continue
            try:
                r.restore(ans)                     # type: ignore[attr-defined]
            except Exception:
                pass                              # 单题恢复失败不拖垮整卷

    def _show_status_in_title(self) -> None:
        assert self._assignment is not None
        suffix = " · 已提交" if self._saved_status == "submitted" else ""
        self._title.setText(f"{self._assignment.title}{suffix}")

    def _show_review_alerts(self) -> None:
        """提交后：每张题卡顶部 Alert 显示自动判分 + 老师批改结果。

        优先级：老师批改（reviews）> 自动判分（report）> 无（未提交不显示）。
        """
        assert self._assignment is not None and self._report is not None
        theme = getattr(self._theme_provider, "theme", "auto")
        report_by_qid = {it.qid: it for it in self._report.items}

        for qid, card in self._cards.items():
            review = self._reviews.get(qid)
            item = report_by_qid.get(qid)

            if review is not None:                     # 老师批改过：批改结果优先
                correct = review.correct
                extra = ""
                if correct is not None:
                    parts = []
                    if correct.selected:
                        parts.append(f"正确选项 {correct.selected}")
                    if correct.values:
                        parts.append("、".join(v or "＿" for v in correct.values))
                    if correct.text:
                        parts.append(correct.text[:60])
                    if correct.source:
                        parts.append(correct.source[:80])
                    if parts:
                        extra = " ｜ 正确答案：" + "；".join(parts)
                if review.comment:
                    extra += f" ｜ 评语：{review.comment}"
                if review.passed:
                    alert = Alert(title="老师批改：通过 ✓", description=extra or "作答正确",
                                   color="success", variant="flat", theme=theme)
                else:
                    alert = Alert(title="老师批改：未通过 ✗", description=extra or "请看正确答案",
                                   color="danger", variant="flat", theme=theme)
            elif item is not None:                     # 自动判分
                vmap = {
                    "correct": ("回答正确", "success"),
                    "partial": ("部分正确", "warning"),
                    "wrong": ("回答错误", "danger"),
                    "unanswered": ("未作答", "warning"),
                    "pending_manual": ("等待老师批改", "default"),
                    "graded_manual": ("已批改", "success"),
                }
                text, color = vmap.get(item.verdict, ("已提交", "default"))
                desc = item.detail or ""
                alert = Alert(title=text, description=desc,
                              color=color, variant="flat", theme=theme)
            else:
                continue

            body = card.property("body_layout")
            if body is not None:
                body.insertWidget(1, alert)            # 题号之后、题干之前

    def _render_tabs(self) -> None:
        assert self._assignment is not None
        theme = getattr(self._theme_provider, "theme", "auto")

        # 官方姿势：Tabs.clear() 清空旧 tab，复用同一个 Tabs 实例
        # （deleteLater 整个 Tabs 会让 cursor 动画组件悬挂引用 → QPainter 崩溃）
        self._tabs.clear()
        self._renderers.clear()
        self._cards.clear()
        self._poll_editors.clear()

        by_type: dict[str, list] = {t: [] for t, _ in TYPE_TABS}
        for q in self._assignment.questions:
            by_type.setdefault(q.type, []).append(q)

        for qtype, tab_title in TYPE_TABS:
            qs = by_type.get(qtype, [])
            if not qs:
                continue                        # 该卷没有的题型不出 Tab

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QScrollArea.Shape.NoFrame)   # 去掉滚动区黑色边框
            host = QWidget()
            hl = QVBoxLayout(host)
            hl.setContentsMargins(4, 4, 4, 4)
            hl.setSpacing(18)

            for no, q in enumerate(qs, start=1):
                renderer = create_renderer(q, theme=theme)
                self._renderers[q.id] = renderer
                self._connect_autosave(renderer, q.id)   # 实时保存信号

                card = Card()                    # 每道题一张 Card
                card.setSizePolicy(              # 垂直不吸收富余高度：题少的 Tab 不再把卡拉高
                    QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum,
                )
                body = CardBody()
                bl = body.layout()
                bl.setContentsMargins(16, 10, 16, 12)         # 上小、下略大，对答题区更友好
                bl.setSpacing(4)

                num = Text(f"第 {no} 题", size="md", weight="medium", theme=theme)
                num.setStyleSheet(                             # 清 QLabel 隐式 padding/margin
                    "QLabel{padding:0px;margin:0px;line-height:1;background:transparent;}"
                )
                bl.addWidget(num)

                stem = Text(q.stem)                          # 还原：纯 Text 渲染题干
                stem.setWordWrap(True)
                bl.addWidget(stem)

                rw = renderer.widget()
                bl.addWidget(rw, 1)                             # 作答区独占所有富余高度
                card.add_body(body)
                card.setProperty("body_layout", bl)     # Alert 插入点（_show_review_alerts 用）
                self._cards[q.id] = card
                hl.addWidget(card)

            hl.addStretch(1)
            scroll.setWidget(host)
            self._tabs.add_tab(f"{tab_title} · {len(qs)} 题", scroll, key=qtype)

    # ------------------------------------------------------------------
    # 收集 / 实时保存 / 提交
    # ------------------------------------------------------------------

    def collect_answers(self) -> dict[str, Answer]:
        return {qid: r.collect() for qid, r in self._renderers.items()}

    # ---- 实时保存：信号 → 防抖 500ms → 落盘 ----

    def _connect_autosave(self, renderer, qid: str) -> None:
        """渲染器内容变化 → 标记 dirty → 防抖写盘。

        注意 CodeEditor 例外：0.8.1 的 text_changed 存在自触发循环
        （rehighlight → textChanged → emit → 150ms 后重扫 → ……），
        信号风暴会把防抖定时器无限重置。编程题改走内容比对轮询。
        """
        if hasattr(renderer, "_editor"):                 # programming：轮询
            self._poll_editors.append(renderer)
            return
        group = getattr(renderer, "_group", None)        # RadioGroup
        if group is not None:
            group.value_changed.connect(lambda _v: self._mark_dirty())
            return
        area = getattr(renderer, "_area", None)          # Textarea
        if area is not None:
            area.text_changed.connect(lambda _t: self._mark_dirty())
            return
        for inp in getattr(renderer, "_inputs", []):     # fill_blank 多个 Input
            inp.text_changed.connect(lambda _t: self._mark_dirty())

    def _poll_programming(self) -> None:
        """编程题低频轮询（2s）：编辑器内容与上次保存快照不同才算脏。"""
        for r in self._poll_editors:
            if r.collect() != self._editor_snapshot.get(id(r)):
                self._mark_dirty()
                break

    def _mark_dirty(self) -> None:
        if self._saved_status == "submitted":
            return                                        # 已提交不再自动保存
        self._dirty = True
        self._save_timer.start()                          # 重置防抖 500ms

    def _flush_save(self) -> None:
        """防抖到期 / 关窗兜底：把当前作答写盘。"""
        if not self._dirty or self._assignment is None:
            return
        if self._saved_status == "submitted" or not self._student_name:
            return
        try:
            save_answers(
                self._answers_file, self._assignment,
                self._student_name, self.collect_answers(),
                status="in_progress",
            )
            self._dirty = False
            # 更新编程题快照，避免轮询立刻再次判脏
            if self._poll_editors:
                self._editor_snapshot = {id(r): r.collect() for r in self._poll_editors}
        except Exception:
            pass                                          # 保存失败不炸 UI

    def closeEvent(self, event) -> None:
        self._flush_save()                                # 关窗兜底
        super().closeEvent(event)

    # ---- 提交 ----

    def _on_submit(self) -> None:
        if self._assignment is None or self._saved_status == "submitted":
            return
        self._flush_save()
        try:
            self._report = submit_answers(
                self._answers_file, self._assignment,
                self._student_name, self.collect_answers(),
            )
            self._saved_status = "submitted"
            self._dirty = False
            self._submit_btn.setEnabled(False)
            self._show_status_in_title()
            # 提交即锁定 + 立刻显示每题判分结果
            for r in self._renderers.values():
                r.set_disabled(True)
            self._show_review_alerts()
        except Exception:
            pass

