"""code_explain 代码解释提渲染器：CodeBlock 代码 + Textarea 自由作答。"""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from hero_side_ui import CodeBlock, Textarea

from core.schema import Answer, CodeExplain, CodeExplainAnswer

from .base import QuestionRenderer


class CodeExplainRenderer(QWidget):
    def __init__(self, question: CodeExplain, theme: str = "auto", parent: QWidget | None = None):
        super().__init__(parent)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        if question.code:
            lay.addWidget(CodeBlock(question.code, language="python"))

        self._area = Textarea(
            placeholder="写下你对这段代码的分析（要点分条写，批改时更清晰）",
            min_rows=6,
            theme=theme,
        )
        lay.addWidget(self._area)

    def widget(self) -> QWidget:
        return self

    def set_disabled(self, disabled: bool = True) -> None:
        """批改模式：禁用文本区。"""
        self._area.set_is_disabled(disabled)

    def collect(self) -> Answer:
        t = self._area.text()
        return CodeExplainAnswer(text=t if t.strip() else None)

    def is_answered(self) -> bool:
        return bool(self._area.text().strip())

    def restore(self, answer: CodeExplainAnswer) -> None:
        self._area.set_text(answer.text or "")
