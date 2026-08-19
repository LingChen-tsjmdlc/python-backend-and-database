"""app.renderers.base —— 渲染器协议：Question → QWidget，可吐出 Answer。"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from PySide6.QtWidgets import QWidget

from core.schema import Answer, Question


@runtime_checkable
class QuestionRenderer(Protocol):
    """所有题型渲染器的协议。

    - ``widget()``       返回可挂进滚动区的控件（题卡内容部分）。
    - ``collect()``      返回当前作答（即使没作答也要返回对应 Answer 类型的空值形态）。
    - ``is_answered()``  是否已有实质作答（用于进度条）。
    """

    def widget(self) -> QWidget: ...

    def collect(self) -> Answer: ...

    def is_answered(self) -> bool: ...
