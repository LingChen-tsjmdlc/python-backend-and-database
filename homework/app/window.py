"""app.window —— 主窗口：左侧章节列表 + 右侧题目滚动区 + 底部进度与提交。"""

from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from hero_side_ui import (
    Button,
    Card,
    CardBody,
    CardHeader,
    Chip,
    HeroSideUIProvider,
    Listbox,
    ListboxItem,
    Progress,
    Subtitle,
    Text,
    ThemeProvider,
    ThemeSwitcher,
    Title,
)

from core.grader import apply_manual_score, grade
from core.loader import LoadResult, discover_assignments, load_assignment
from core.schema import (
    Answer,
    Assignment,
    GradeReport,
    ManualScore,
    ProgrammingAnswer,
)

from .renderers import create_renderer
from .renderers.base import QuestionRenderer

ROOT = Path(__file__).resolve().parent.parent
BANK_ROOT = ROOT                       # 题库根：homework/（扫描 part*/section*.yaml）
SUBMISSIONS = ROOT / "submissions"

TYPE_LABEL = {
    "single_choice": "单选",
    "fill_blank": "填空",
    "code_explain": "代码解析",
    "programming": "编程",
}


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("作业 · homework-studio")
        self.resize(1180, 800)

        self._theme_provider = ThemeProvider.instance()

        self._results: list[LoadResult] = []
        self._assignment: Assignment | None = None
        self._renderers: dict[str, QuestionRenderer] = {}
        self._report: GradeReport | None = None

        self._build_ui()
        self._load_bank()

    # ------------------------------------------------------------------
    # UI 构建
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        root.addWidget(self._build_sidebar())

        right = QVBoxLayout()
        right.setSpacing(10)
        right.addWidget(self._build_header(), stretch=0)
        right.addWidget(self._build_scroll(), stretch=1)
        right.addWidget(self._build_footer(), stretch=0)
        root.addLayout(right, stretch=1)

    def _build_sidebar(self) -> QWidget:
        side = QVBoxLayout()
        side.setSpacing(8)

        side.addWidget(Title("章节", level=3))

        self._listbox = Listbox(selection_mode="single", disallow_empty_selection=True)
        self._listbox.selection_changed.connect(self._on_section_picked)
        side.addWidget(self._listbox, stretch=1)

        side.addWidget(ThemeSwitcher())
        w = QWidget()
        w.setLayout(side)
        w.setFixedWidth(230)
        return w

    def _build_header(self) -> QWidget:
        row = QHBoxLayout()
        self._title = Title("选择一个章节开始", level=1)
        row.addWidget(self._title, stretch=1)
        self._points_chip = Chip("总分 0", variant="flat")
        row.addWidget(self._points_chip)
        w = QWidget()
        w.setLayout(row)
        return w

    def _build_scroll(self) -> QWidget:
        self._cards_host = QWidget()
        self._cards_lay = QVBoxLayout(self._cards_host)
        self._cards_lay.setContentsMargins(4, 4, 4, 4)
        self._cards_lay.setSpacing(14)
        self._cards_lay.addStretch(1)

        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(self._cards_host)
        area.setObjectName("cardsScroll")
        return area

    def _build_footer(self) -> QWidget:
        foot = QVBoxLayout()
        foot.setSpacing(6)

        prog_row = QHBoxLayout()
        self._progress = Progress(value=0, show_value_label=True, size="sm")
        prog_row.addWidget(self._progress, stretch=1)
        foot.addLayout(prog_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self._submit_btn = Button("提交整卷", color="primary", variant="solid")
        self._submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(self._submit_btn)
        foot.addLayout(btn_row)

        w = QWidget()
        w.setLayout(foot)
        return w

    # ------------------------------------------------------------------
    # 数据加载
    # ------------------------------------------------------------------

    def _load_bank(self) -> None:
        banks = sorted(BANK_ROOT.glob("part*/section*.yaml"))
        self._results = [load_assignment(p) for p in banks]

        for res in self._results:
            a = res.assignment
            self._listbox.add_item(ListboxItem(
                title=a.title,
                key=a.id,
                description=f"{len(a.questions)} 题 · {a.total_points} 分",
            ))
        if self._results:
            first = self._results[0].assignment.id
            self._listbox.set_selected_keys([first])

    # ------------------------------------------------------------------
    # 章节切换
    # ------------------------------------------------------------------

    def _on_section_picked(self, _keys=None) -> None:
        selected = self._listbox.selected_keys()
        if not selected:
            return
        aid = next(iter(selected))          # selected_keys() 返回 set
        res = next((r for r in self._results if r.assignment.id == aid), None)
        if res is None:
            return
        self._assignment = res.assignment
        self._report = None
        self._render_title()
        self._render_questions()

    def _render_title(self) -> None:
        assert self._assignment is not None
        self._title.setText(self._assignment.title)
        self._points_chip.set_text(f"总分 {self._assignment.total_points}")

    def _render_questions(self) -> None:
        assert self._assignment is not None
        theme = self._theme_provider.theme if hasattr(self._theme_provider, "theme") else "auto"

        # 清空旧卡
        while self._cards_lay.count():
            item = self._cards_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        self._renderers.clear()
        for idx, q in enumerate(self._assignment.questions, start=1):
            renderer = create_renderer(q, theme=theme)
            self._renderers[q.id] = renderer

            card = Card()
            body = CardBody()
            bl = body.layout()
            bl.setContentsMargins(16, 12, 16, 12)
            bl.setSpacing(10)

            head = QHBoxLayout()
            head.addWidget(Subtitle(f"第 {idx} 题 · {TYPE_LABEL.get(q.type, q.type)} · {q.points} 分"))
            head.addStretch(1)
            bl.addLayout(head)

            stem = Text(q.stem)
            stem.setWordWrap(True)
            bl.addWidget(stem)

            bl.addWidget(renderer.widget())

            card.add_body(body)
            self._cards_lay.addWidget(card)

        self._cards_lay.addStretch(1)
        self._update_progress()

    # ------------------------------------------------------------------
    # 进度 / 收集 / 提交
    # ------------------------------------------------------------------

    def _update_progress(self) -> None:
        if not self._renderers:
            self._progress.set_value(0)
            return
        n = sum(1 for r in self._renderers.values() if r.is_answered())
        total = len(self._renderers)
        self._progress.set_value(n / total * 100)

    def collect_answers(self) -> dict[str, Answer]:
        return {qid: r.collect() for qid, r in self._renderers.items()}

    def _on_submit(self) -> None:
        if self._assignment is None:
            return
        answers = self.collect_answers()

        # 编程题：提交时把学员文件复制归档，判分读归档副本
        for qid, ans in list(answers.items()):
            if isinstance(ans, ProgrammingAnswer) and ans.file:
                src = Path(ans.file)
                if src.is_file():
                    dst_dir = SUBMISSIONS / self._assignment.id / qid
                    dst_dir.mkdir(parents=True, exist_ok=True)
                    dst = dst_dir / "answer.py"
                    shutil.copy2(src, dst)
                    answers[qid] = ProgrammingAnswer(file=str(dst))

        self._report = grade(self._assignment, answers)
        self._show_report()

    def _show_report(self) -> None:
        """P5 会做完整结果页；骨架期先弹摘要（用标题区显示）。"""
        assert self._report is not None
        r = self._report
        pending = r.manual.total - r.manual.earned
        self._title.setText(
            f"自动题 {r.auto.earned:.0f}/{r.auto.total:.0f} 分 · "
            f"待批改 {pending:.0f} 分 · 已得 {r.grand_total_earned:.0f} 分"
        )
        self._update_progress()
