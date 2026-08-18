"""core —— 题库加载 / 校验 / 学员文件解析 / 判分（纯逻辑，零 Qt 依赖）。"""

from .schema import (
    Answer,
    Assignment,
    Blank,
    CodeExplain,
    CodeExplainAnswer,
    FillBlank,
    FillBlankAnswer,
    ItemResult,
    ManualScore,
    Option,
    ParseResult,
    Programming,
    ProgrammingAnswer,
    Question,
    SingleChoice,
    SingleChoiceAnswer,
    Verdict,
)
from .loader import EXPECTED_TOTAL, LoadResult, SchemaError, discover_assignments, load_assignment
from .parse import MAX_FILE_BYTES, ParseFileError, parse_py_file
from .grader import AUTO_TYPES, MANUAL_TYPES, apply_manual_score, grade

__all__ = [
    "Answer", "Assignment", "Blank", "CodeExplain", "CodeExplainAnswer",
    "FillBlank", "FillBlankAnswer", "ItemResult", "ManualScore", "Option",
    "ParseResult", "Programming", "ProgrammingAnswer", "Question",
    "SingleChoice", "SingleChoiceAnswer", "Verdict",
    "EXPECTED_TOTAL", "LoadResult", "SchemaError", "discover_assignments", "load_assignment",
    "MAX_FILE_BYTES", "ParseFileError", "parse_py_file",
    "AUTO_TYPES", "MANUAL_TYPES", "apply_manual_score", "grade",
]
