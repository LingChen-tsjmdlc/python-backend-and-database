"""single_choice 渲染器：选项 RadioGroup；代码分析题带 CodeBlock 代码上下文。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from hero_side_ui import CodeBlock, RadioGroup

from core.schema import Answer, SingleChoice, SingleChoiceAnswer

from .base import QuestionRenderer


class SingleChoiceRenderer(QWidget):
    def __init__(self, question: SingleChoice, theme: str = "auto", parent: QWidget | None = None):
        super().__init__(parent)
        self._q = question

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        if question.code:
            self._code = CodeBlock(question.code, language="python")
            lay.addWidget(self._code)
        else:
            self._code = None

        self._group = RadioGroup(orientation="vertical", theme=theme)
        for opt in question.options:
            self._group.create_radio(f"{opt.key}. {opt.text}", value=opt.key)
        lay.addWidget(self._group)

    def widget(self) -> QWidget:
        return self

    def collect(self) -> Answer:
        v = self._group.value()
        return SingleChoiceAnswer(selected=v if v else None)

    def is_answered(self) -> bool:
        return bool(self._group.value())

    def set_theme(self, theme: str) -> None:
        """切主题时重建（状态由 collect/restore 承接）。"""
        current = self.collect()
        old, self._group = self._group, RadioGroup(orientation="vertical", theme=theme)
        for opt in self._q.options:
            self._group.create_radio(f"{opt.key}. {opt.text}", value=opt.key)
        if current.selected:
            self._group.set_value(current.selected)
        lay = self.layout()
        lay.replaceWidget(old, self._group)
        old.deleteLater()

    def restore(self, answer: SingleChoiceAnswer) -> None:
        if answer.selected:
            self._group.set_value(answer.selected)
