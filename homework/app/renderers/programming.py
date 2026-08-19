"""programming 渲染器：CodeEditor 直写代码作答。

- starter 作为编辑器预填内容（学员可直接在其上写）。
- 提交时把编辑器全文落盘到 submissions/<卷>/<题>/answer.py 再判分。
"""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from hero_side_ui import CodeEditor

from core.schema import Answer, Programming, ProgrammingAnswer

from .base import QuestionRenderer


class ProgrammingRenderer(QWidget):
    def __init__(self, question: Programming, theme: str = "auto", parent: QWidget | None = None):
        super().__init__(parent)
        self._q = question
        self._starter = (question.starter or "").strip()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        self._editor = CodeEditor(
            value=question.starter or "",
            language="python",
            min_lines=12,
            theme=theme,
        )
        lay.addWidget(self._editor)

    def widget(self) -> QWidget:
        return self

    def set_disabled(self, disabled: bool = True) -> None:
        """批改模式：编辑器只读（仍可选中复制）。"""
        self._editor.set_read_only(disabled)

    def collect(self) -> Answer:
        current = self._editor.value()
        # starter 原样未动 → 视为未作答（不落盘、判 unanswered）
        if current.strip() == self._starter:
            return ProgrammingAnswer(file=None, source=None)
        return ProgrammingAnswer(file=None, source=current)

    def is_answered(self) -> bool:
        current = self._editor.value().strip()
        return bool(current) and current != self._starter

    def restore(self, answer: ProgrammingAnswer) -> None:
        text = answer.source if answer.source is not None else ""
        self._editor.set_value(text or (self._q.starter or ""))

