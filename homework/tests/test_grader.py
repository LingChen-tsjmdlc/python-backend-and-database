"""grader 测试（无分数口径）：自动题对错 / 手动题批阅流转。"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.grader import apply_manual_review, grade
from core.loader import load_assignment
from core.schema import (
    CodeExplainAnswer,
    FillBlankAnswer,
    ManualReview,
    ProgrammingAnswer,
    SingleChoiceAnswer,
)

from .conftest import AUTO_TOTAL, MANUAL_TOTAL


@pytest.fixture
def assignment(assignment_yaml: Path):
    return load_assignment(assignment_yaml).assignment


# ---------------------------------------------------------------------------
# 自动题
# ---------------------------------------------------------------------------


def test_all_auto_correct(assignment, good_py: Path):
    r = grade(assignment, {
        "sc-01": SingleChoiceAnswer(selected="C"),
        "ca-01": SingleChoiceAnswer(selected="B"),
        "fb-01": FillBlankAnswer(values=("5", "float")),
        "ce-01": CodeExplainAnswer(text="计算平均值"),
        "pg-01": ProgrammingAnswer(file=str(good_py)),
    })
    assert r.auto_correct == AUTO_TOTAL == 3
    assert r.auto_total == 3
    assert r.auto_wrong == 0
    sc = next(it for it in r.items if it.qid == "sc-01")
    assert sc.verdict == "correct"


def test_fill_blank_accept_alias(assignment):
    r = grade(assignment, {
        "fb-01": FillBlankAnswer(values=("5", "<class 'float'>")),
    })
    fb = next(it for it in r.items if it.qid == "fb-01")
    assert fb.verdict == "correct"


def test_fill_blank_partial(assignment):
    r = grade(assignment, {"fb-01": FillBlankAnswer(values=("5", "int"))})
    fb = next(it for it in r.items if it.qid == "fb-01")
    assert fb.verdict == "partial"
    assert r.auto_partial == 1
    assert r.auto_correct == 0


def test_fill_blank_strip(assignment):
    r = grade(assignment, {"fb-01": FillBlankAnswer(values=("  5  ", "float "))})
    fb = next(it for it in r.items if it.qid == "fb-01")
    assert fb.verdict == "correct"


def test_single_choice_wrong_counts_wrong(assignment):
    r = grade(assignment, {"sc-01": SingleChoiceAnswer(selected="A")})
    sc = next(it for it in r.items if it.qid == "sc-01")
    assert sc.verdict == "wrong"
    assert r.auto_wrong == 1


def test_unanswered_all_flagged(assignment):
    r = grade(assignment, {})
    assert all(it.verdict == "unanswered" for it in r.items)
    assert r.auto_correct == 0 and r.auto_total == 3
    assert r.manual_pending == 0          # 没作答的不算待批
    assert r.manual_total == MANUAL_TOTAL


def test_blank_string_counts_as_unanswered(assignment):
    r = grade(assignment, {"sc-01": SingleChoiceAnswer(selected="   ")})
    sc = next(it for it in r.items if it.qid == "sc-01")
    assert sc.verdict == "unanswered"


def test_unknown_qid_ignored(assignment):
    r = grade(assignment, {"sc-01": SingleChoiceAnswer(selected="C"),
                           "ghost-99": SingleChoiceAnswer(selected="A")})
    assert r.auto_correct == 1


# ---------------------------------------------------------------------------
# 手动题流转
# ---------------------------------------------------------------------------


def test_manual_pending_then_reviewed(assignment, good_py: Path):
    r = grade(assignment, {
        "ce-01": CodeExplainAnswer(text="计算平均值，命名不清晰"),
        "pg-01": ProgrammingAnswer(file=str(good_py)),
    })
    ce = next(it for it in r.items if it.qid == "ce-01")
    pg = next(it for it in r.items if it.qid == "pg-01")
    assert ce.verdict == "pending_manual" and ce.passed is None
    assert pg.verdict == "pending_manual"
    assert r.manual_pending == 2

    r2 = apply_manual_review(r, ManualReview(qid="ce-01", passed=True, comment="要点到位"))
    ce2 = next(it for it in r2.items if it.qid == "ce-01")
    assert ce2.verdict == "graded_manual" and ce2.passed is True
    assert ce2.detail == "要点到位"
    assert r2.manual_graded == 1 and r2.manual_passed == 1

    # 原报告不可变
    assert ce.earned if False else ce.passed is None


def test_programming_syntax_error_recorded(assignment, syntax_err_py: Path):
    r = grade(assignment, {"pg-01": ProgrammingAnswer(file=str(syntax_err_py))})
    pg = next(it for it in r.items if it.qid == "pg-01")
    assert pg.verdict == "pending_manual"          # 语法错也只是提示，仍走人工
    assert pg.parse_result.ok is False
    assert "语法错误" in pg.detail


def test_programming_editor_source_grading(assignment):
    r = grade(assignment, {
        "pg-01": ProgrammingAnswer(source="def bmi(w, h):\n    return round(w / h ** 2, 1)\n"),
    })
    pg = next(it for it in r.items if it.qid == "pg-01")
    assert pg.verdict == "pending_manual"
    assert pg.parse_result.ok
    assert "bmi" in pg.parse_result.defs


# ---------------------------------------------------------------------------
# apply_manual_review 防呆
# ---------------------------------------------------------------------------


def test_review_unknown_qid(assignment, good_py: Path):
    r = grade(assignment, {"pg-01": ProgrammingAnswer(file=str(good_py))})
    with pytest.raises(KeyError):
        apply_manual_review(r, ManualReview(qid="ghost", passed=True))


def test_review_auto_question_rejected(assignment):
    r = grade(assignment, {"sc-01": SingleChoiceAnswer(selected="C")})
    with pytest.raises(ValueError, match="不是手动题"):
        apply_manual_review(r, ManualReview(qid="sc-01", passed=True))


def test_review_unanswered_rejected(assignment):
    r = grade(assignment, {})
    with pytest.raises(ValueError, match="未作答"):
        apply_manual_review(r, ManualReview(qid="ce-01", passed=True))


def test_double_review_rejected(assignment, good_py: Path):
    r = grade(assignment, {"pg-01": ProgrammingAnswer(file=str(good_py))})
    r2 = apply_manual_review(r, ManualReview(qid="pg-01", passed=False))
    with pytest.raises(ValueError, match="不能再批阅"):
        apply_manual_review(r2, ManualReview(qid="pg-01", passed=True))
