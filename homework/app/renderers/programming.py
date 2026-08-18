"""programming 渲染器：starter CodeBlock + 选 .py 文件（Button + QFileDialog + 文件名 Chip）。

提交时机由主窗口控制：渲染器只负责选择与展示，文件复制归档在提交时统一做。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QWidget

from hero_side_ui import Button, Chip, CodeBlock

from core.schema import Answer, Programming, ProgrammingAnswer

from .base import QuestionRenderer


class ProgrammingRenderer(QWidget):
    def __init__(self, question: Programming, theme: str = "auto", parent: QWidget | None = None):
        super().__init__(parent)
        self._q = question
        self._file: Path | None = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        if question.starter:
            lay.addWidget(CodeBlock(question.starter, language="python"))

        row = QHBoxLayout()
        row.setSpacing(8)
        self._pick_btn = Button("选择 .py 文件", color="primary", variant="flat", theme=theme)
        self._pick_btn.clicked.connect(self._on_pick)
        row.addWidget(self._pick_btn)

        self._chip = Chip("", color="success", variant="flat")
        self._chip.hide()
        row.addWidget(self._chip)
        row.addStretch(1)
        lay.addLayout(row)

    def _on_pick(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "选择答案文件", "", "Python 文件 (*.py)"
        )
        if not path:
            return
        p = Path(path)
        if p.suffix.lower() != ".py":
            self._chip.set_text("只接受 .py 文件")
            self._chip.setStyleSheet("color: #f31260;")
            self._chip.show()
            return
        self._file = p
        self._chip.set_text(p.name)
        self._chip.setStyleSheet("")
        self._chip.show()

    def widget(self) -> QWidget:
        return self

    def collect(self) -> Answer:
        return ProgrammingAnswer(file=str(self._file) if self._file else None)

    def is_answered(self) -> bool:
        return self._file is not None

    def restore(self, answer: ProgrammingAnswer) -> None:
        if answer.file and Path(answer.file).suffix.lower() == ".py":
            self._file = Path(answer.file)
            self._chip.set_text(self._file.name)
            self._chip.show()
