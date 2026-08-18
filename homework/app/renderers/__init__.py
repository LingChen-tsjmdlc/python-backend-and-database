"""渲染器注册表：type → 工厂。新题型在此登记，core 与主窗口零改动。"""

from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QWidget

from core.schema import (
    CodeExplain,
    FillBlank,
    Programming,
    Question,
    SingleChoice,
)

from .base import QuestionRenderer
from .code_explain import CodeExplainRenderer
from .fill_blank import FillBlankRenderer
from .programming import ProgrammingRenderer
from .single_choice import SingleChoiceRenderer

RendererFactory = Callable[..., QWidget]


def _factories() -> dict[str, RendererFactory]:
    return {
        "single_choice": SingleChoiceRenderer,
        "fill_blank": FillBlankRenderer,
        "code_explain": CodeExplainRenderer,
        "programming": ProgrammingRenderer,
    }


RENDERERS: dict[str, RendererFactory] = _factories()


def create_renderer(question: Question, theme: str = "auto") -> QuestionRenderer:
    """按题型创建渲染器；未知题型抛 ValueError（schema 已限制，理论不可达）。"""
    try:
        cls = RENDERERS[question.type]
    except KeyError:
        raise ValueError(f"没有注册的渲染器: {question.type}") from None
    return cls(question, theme=theme)  # type: ignore[call-arg]


__all__ = ["RENDERERS", "create_renderer", "QuestionRenderer"]
