"""批改页：作业页的镜像 —— 同样的题目卡片 + 学生答案回填 + 全控件禁用
+ 每题下方的批改按钮（✓/×）与"批错时的正确答案"编辑组件。

布局与作业页同构：左侧（返回 + 学生 Select），右侧四个题型 Tabs，
每张题卡：题号 → 题干 → 学生作答区（渲染器回填后禁用）→ 批改控件。

数据全部落同一份 /<学生>/section*.yaml 的 reviews 段。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from hero_side_ui import (
    Button,
    Card,
    CardBody,
    CodeEditor,
    Divider,
    Input,
    Select,
    Tabs,
    Text,
    Textarea,
    Title,
)

from core.answers import list_students, load_answers, save_review, student_answers_path
from core.loader import load_assignment
from core.schema import (
    Answer,
    Assignment,
    CorrectAnswer,
    ManualReview,
)

from .paths import BANK_ROOT
from .renderers import create_renderer

# 四个题型 Tab（与作业页一致）
TYPE_TABS = [
    ("single_choice", "单选 · 代码分析"),
    ("fill_blank", "填空"),
    ("code_explain", "代码解析"),
    ("programming", "编程"),
]


class GradePage(QWidget):
    """批改主页面（MainWindow stack 页 3）。"""

    def __init__(self, stack, theme_provider, parent=None):
        super().__init__(parent)
        self._stack = stack
        self._theme_provider = theme_provider

        self._assignment: Assignment | None = None
        self._bank_yaml: Path | None = None
        self._student = ""
        self._answers: dict[str, Answer] = {}
        self._status = ""
        self._reviews: dict[str, ManualReview] = {}
        self._renderers: dict = {}              # qid -> 渲染器（禁用态）
        self._correct_widgets: dict[str, QWidget] = {}

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(16)

        # 左：返回 + 学生选择 + 题库目录（与作业页同构）
        side = QVBoxLayout()
        side.setSpacing(8)
        side.addWidget(Title("批改", level=3))

        back = Button("← 返回")
        back.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        side.addWidget(back)

        self._student_sel = Select(placeholder="选择学生", items=[], size="sm")
        self._student_sel.selection_changed.connect(self._on_student_picked)
        side.addWidget(self._student_sel)

        # 题库目录（可滚动）：六个部分 + 作业按钮
        self._bank_host = QWidget()
        self._bank_lay = QVBoxLayout(self._bank_host)
        self._bank_lay.setContentsMargins(0, 0, 0, 0)
        self._bank_lay.setSpacing(6)
        bank_scroll = QScrollArea()
        bank_scroll.setWidgetResizable(True)
        bank_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        bank_scroll.setWidget(self._bank_host)
        side.addWidget(bank_scroll, stretch=1)

        side_w = QWidget()
        side_w.setLayout(side)
        side_w.setFixedWidth(240)
        root.addWidget(side_w, stretch=0)

        root.addWidget(Divider(orientation="vertical"))

        # 右：提示 / 题目 Tabs（Tabs 拿全部 stretch，Tab 下内容撑满）
        self._hint = Text("从左侧选择学生开始批改", size="lg")
        self._tabs = Tabs()
        self._right = QVBoxLayout()
        self._right.setContentsMargins(0, 0, 0, 0)
        self._right.addWidget(self._hint)
        self._right.addWidget(self._tabs, stretch=1)   # 永久占位，撑满右侧

        right_w = QWidget()
        right_w.setLayout(self._right)
        root.addWidget(right_w, stretch=1)

    # ------------------------------------------------------------------
    # 进入页面：加载题库 + 刷新学生名单
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """进入批改页：加载题库目录 + 刷新学生名单。"""
        self._load_bank_list()
        if self._assignment is None:
            self._pick_first_bank()
        students = list_students(self._bank_yaml) if self._bank_yaml else []
        self._student_sel.set_items([{"key": s, "label": s} for s in students])

    def _load_bank_list(self) -> None:
        """侧栏题库目录（一次性构建）：部分标题 + 分割线 + 作业按钮。"""
        if getattr(self, "_bank_list_built", False):
            return
        self._bank_list_built = True
        from .paths import PART_LABELS

        for part_idx, (part_dir, part_label) in enumerate(PART_LABELS.items()):
            banks = sorted((BANK_ROOT / part_dir).glob("section*.yaml"))
            if part_idx > 0:
                self._bank_lay.addSpacing(4)
                sep = Divider()
                sep.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
                )
                self._bank_lay.addWidget(sep)
                self._bank_lay.addSpacing(4)

            label = Text(part_label, size="lg")
            label.setWordWrap(True)
            self._bank_lay.addWidget(label)

            for p in banks:
                from core.loader import load_assignment as _load
                try:
                    a = _load(p).assignment
                except Exception:
                    continue
                btn = Button(
                    a.title, color="primary", variant="flat", size="sm",
                    full_width=True,
                )
                btn.clicked.connect(
                    lambda _=False, bp=str(p): self._on_bank_picked(bp)
                )
                self._bank_lay.addWidget(btn)

        self._bank_lay.addStretch(1)

    def _pick_first_bank(self) -> None:
        banks = sorted(BANK_ROOT.glob("part*/section*.yaml"))
        if banks:
            self._bank_yaml = banks[0]
            self._assignment = load_assignment(self._bank_yaml).assignment

    def _on_bank_picked(self, bank_path: str) -> None:
        """切换作业：重载题库 + 刷新学生名单。"""
        self._bank_yaml = Path(bank_path)
        self._assignment = load_assignment(self._bank_yaml).assignment
        students = list_students(self._bank_yaml)
        self._student_sel.set_items([{"key": s, "label": s} for s in students])
        # 学生选择重置为空，等下一次选择
        self._student_sel.set_selected_keys(set())

    def _on_student_picked(self, key) -> None:
        if not key or self._assignment is None or self._bank_yaml is None:
            return
        self._student = key
        path = student_answers_path(self._bank_yaml, self._student)
        self._answers, self._status, _report, self._reviews = load_answers(
            path, self._assignment
        )
        self._render_tabs()

    # ------------------------------------------------------------------
    # 题目渲染（与作业页同构 + 禁用 + 批改控件）
    # ------------------------------------------------------------------

    def _render_tabs(self) -> None:
        assert self._assignment is not None
        theme = getattr(self._theme_provider, "theme", "auto")

        # 换 hint 为 tabs
        self._hint.hide()
        self._tabs.clear()
        self._renderers.clear()
        self._correct_widgets.clear()

        by_type: dict[str, list] = {t: [] for t, _ in TYPE_TABS}
        for q in self._assignment.questions:
            by_type.setdefault(q.type, []).append(q)

        for qtype, tab_title in TYPE_TABS:
            qs = by_type.get(qtype, [])
            if not qs:
                continue

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QScrollArea.Shape.NoFrame)
            host = QWidget()
            hl = QVBoxLayout(host)
            hl.setContentsMargins(4, 4, 4, 4)
            hl.setSpacing(18)

            for no, q in enumerate(qs, start=1):
                renderer = create_renderer(q, theme=theme)
                self._renderers[q.id] = renderer

                # 回填学生答案
                saved = self._answers.get(q.id)
                if saved is not None:
                    try:
                        renderer.restore(saved)
                    except Exception:
                        pass

                # 学生控件全部禁用
                renderer.set_disabled(True)

                card = Card()
                card.setSizePolicy(                  # 撑满：卡片随容器拉伸（内容贴底不留大空白）
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding,
                )
                body = CardBody()
                bl = body.layout()
                bl.setContentsMargins(16, 10, 16, 12)
                bl.setSpacing(8)

                num = Text(f"第 {no} 题", size="md", weight="medium", theme=theme)
                num.setStyleSheet(
                    "QLabel{padding:0px;margin:0px;line-height:1;background:transparent;}"
                )
                bl.addWidget(num)

                stem = Text(q.stem)
                stem.setWordWrap(True)
                bl.addWidget(stem)

                # 学生作答区（禁用态渲染器）：吃掉卡内富余高度，撑满卡片
                bl.addWidget(renderer.widget(), 1)

                # 批改控件
                bl.addWidget(self._review_controls(q, theme))

                card.add_body(body)
                hl.addWidget(card, 1)                # 均分剩余高度：题目再少也撑满整屏

            scroll.setWidget(host)
            self._tabs.add_tab(f"{tab_title} · {len(qs)} 题", scroll, key=qtype)

        # Tabs 在 _build_ui 已带 stretch=1 常驻右侧，这里只藏提示
        self._hint.hide()

    # ------------------------------------------------------------------
    # 批改控件：✓/× + 正确答案编辑区
    # ------------------------------------------------------------------

    def _review_controls(self, q, theme: str) -> QWidget:
        wrap = QWidget()
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(8)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        ok_btn = Button("✓ 正确", color="success", variant="flat", size="sm")
        bad_btn = Button("✗ 错误", color="danger", variant="flat", size="sm")
        btns.addWidget(ok_btn)
        btns.addWidget(bad_btn)
        btns.addStretch(1)
        wl.addLayout(btns)

        correct_host = QWidget()
        cl = QVBoxLayout(correct_host)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(6)
        correct_widget = self._correct_editor(q, theme)
        self._correct_widgets[q.id] = correct_widget
        cl.addWidget(correct_widget)
        correct_host.hide()
        wl.addWidget(correct_host)

        qid = q.id

        ok_btn.clicked.connect(lambda: self._commit_pass(qid, True))
        ok_btn.clicked.connect(lambda: correct_host.hide())
        bad_btn.clicked.connect(lambda: correct_host.show())

        # 已有批改记录 → 恢复
        prev = self._reviews.get(qid)
        if prev is not None:
            if prev.correct is not None:
                self._fill_correct(correct_widget, q.type, prev.correct)
            if not prev.passed and prev.correct is not None:
                correct_host.show()

        wrap._correct_host = correct_host
        return wrap

    def _correct_editor(self, q, theme: str) -> QWidget:
        if q.type == "single_choice":
            sel = Select(
                items=[{"key": o.key, "label": f"{o.key}. {o.text}"}
                       for o in q.options],
                placeholder="选择正确选项",
                size="sm",
                theme=theme,
            )
            sel.selection_changed.connect(
                lambda k, qid=q.id: self._on_correct_changed(qid)
            )
            return sel
        if q.type == "fill_blank":
            host = QWidget()
            hl = QHBoxLayout(host)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(8)
            for i in range(len(q.blanks)):
                inp = Input(placeholder=f"第 {i + 1} 空正确答案", size="sm")
                inp._blank_idx = i
                inp.text_changed.connect(
                    lambda _t, qid=q.id: self._on_correct_changed(qid)
                )
                hl.addWidget(inp)
            return host
        if q.type == "code_explain":
            area = Textarea(placeholder="示范回答", size="sm")
            area.text_changed.connect(
                lambda _t, qid=q.id: self._on_correct_changed(qid)
            )
            return area
        # programming：CodeEditor 不连 text_changed（BUG-004 信号风暴）
        ed = CodeEditor(min_lines=8, theme=theme)
        ed._review_qid = q.id
        self._poll_targets = getattr(self, "_poll_targets", [])
        self._poll_targets.append(ed)
        return ed

    def _fill_correct(self, widget, qtype: str, correct: CorrectAnswer) -> None:
        if qtype == "single_choice" and correct.selected:
            widget.set_selected_key(correct.selected)
        elif qtype == "fill_blank":
            for inp in widget.findChildren(Input):
                i = getattr(inp, "_blank_idx", None)
                if i is not None and i < len(correct.values):
                    inp.set_text(correct.values[i] or "")
        elif qtype == "code_explain" and correct.text:
            widget.set_value(correct.text)
        elif qtype == "programming" and correct.source:
            widget.set_value(correct.source)

    # ------------------------------------------------------------------
    # 写回
    # ------------------------------------------------------------------

    def _collect_correct(self, qid: str) -> CorrectAnswer | None:
        editor = self._correct_widgets.get(qid)
        if editor is None or self._assignment is None:
            return None
        q = self._assignment.question(qid)
        if q.type == "single_choice":
            k = editor.selected_key()
            return CorrectAnswer(selected=k) if k else None
        if q.type == "fill_blank":
            vals = tuple(inp.text() or None for inp in editor.findChildren(Input))
            return CorrectAnswer(values=vals) if any(vals) else None
        if q.type == "code_explain":
            t = editor.value()
            return CorrectAnswer(text=t) if t.strip() else None
        src = editor.value()
        return CorrectAnswer(source=src) if src.strip() else None

    def _on_correct_changed(self, qid: str) -> None:
        correct = self._collect_correct(qid)
        if correct is not None:
            self._upsert(qid, passed=False, correct=correct)

    def _commit_pass(self, qid: str, passed: bool) -> None:
        # 点 ✓：不写 correct（学生已对）；点 × 只标错，correct 由编辑区填写时落
        self._upsert(qid, passed=passed, correct=None)

    def _upsert(self, qid: str, passed: bool, correct: CorrectAnswer | None) -> None:
        # 保留已有 correct（× 之后编辑时别把已填内容冲掉）
        prev = self._reviews.get(qid)
        merged = correct if correct is not None else (prev.correct if prev else None)
        self._reviews[qid] = ManualReview(qid=qid, passed=passed, correct=merged)
        self._persist(qid)

    def _persist(self, qid: str) -> None:
        if not (self._assignment and self._bank_yaml and self._student):
            return
        try:
            save_review(
                student_answers_path(self._bank_yaml, self._student),
                self._assignment, self._student,
                self._answers, self._status, self._reviews[qid],
            )
        except Exception:
            pass
