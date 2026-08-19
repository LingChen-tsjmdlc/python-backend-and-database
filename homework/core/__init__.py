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
    ManualReview,
    Option,
    ParseResult,
    Programming,
    ProgrammingAnswer,
    Question,
    SingleChoice,
    SingleChoiceAnswer,
    Verdict,
)
from .loader import LoadResult, SchemaError, discover_assignments, load_assignment
from .parse import MAX_FILE_BYTES, ParseFileError, parse_py_file
from .grader import AUTO_TYPES, MANUAL_TYPES, apply_manual_review, grade
from .answers import (sanitize_name, save_answers, save_review, load_answers,
                      submit_answers, student_answers_path, list_students)

__all__ = [
    "Answer", "Assignment", "Blank", "CodeExplain", "CodeExplainAnswer",
    "FillBlank", "FillBlankAnswer", "ItemResult", "ManualReview", "Option",
    "ParseResult", "Programming", "ProgrammingAnswer", "Question",
    "SingleChoice", "SingleChoiceAnswer", "Verdict",
    "LoadResult", "SchemaError", "discover_assignments", "load_assignment",
    "MAX_FILE_BYTES", "ParseFileError", "parse_py_file", "parse_py_source",
    "AUTO_TYPES", "MANUAL_TYPES", "apply_manual_review", "grade",
    "sanitize_name", "save_answers", "save_review", "load_answers",
    "submit_answers", "student_answers_path", "list_students",
]
