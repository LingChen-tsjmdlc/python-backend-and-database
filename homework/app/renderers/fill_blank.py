"""fill_blank 渲染器：每个空一个 Input；多空用两列网格排布。"""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QWidget

from hero_side_ui import Input

from core.schema import Answer, FillBlank, FillBlankAnswer

from .base import QuestionRenderer


class FillBlankRenderer(QWidget):
    def __init__(self, question: FillBlank, theme: str = "auto", parent: QWidget | None = None):
        super().__init__(parent)
        self._q = question
        self._inputs: list[Input] = []

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setHorizontalSpacing(10)
        lay.setVerticalSpacing(8)

        for i, blank in enumerate(question.blanks):
            inp = Input(
                placeholder=f"第 {i + 1} 空",
                variant="flat",
                theme=theme,
            )
            self._inputs.append(inp)
            lay.addWidget(inp, i // 2, i % 2)

        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 1)

    def widget(self) -> QWidget:
        return self

    def collect(self) -> Answer:
        values = tuple(
            inp.text() if inp.text().strip() else None
            for inp in self._inputs
        )
        return FillBlankAnswer(values=values)

    def is_answered(self) -> bool:
        return any(inp.text().strip() for inp in self._inputs)

    def restore(self, answer: FillBlankAnswer) -> None:
        for inp, v in zip(self._inputs, answer.values):
            inp.setText(v or "")
