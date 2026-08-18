"""grader 测试：自动题判分 / 未作答 / 手动题流转 / 人工给分写回。"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.grader import apply_manual_score, grade
from core.loader import load_assignment
from core.schema import (
    CodeExplainAnswer,
    FillBlankAnswer,
    ManualScore,
    ProgrammingAnswer,
    SingleChoiceAnswer,
)

from .conftest import AUTO_TOTAL, MANUAL_TOTAL, TOTAL_POINTS


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
    assert r.auto.earned == AUTO_TOTAL == 11
    assert r.auto.total == AUTO_TOTAL
    sc = next(it for it in r.items if it.qid == "sc-01")
    assert sc.verdict == "correct" and sc.earned == 4
    fb = next(it for it in r.items if it.qid == "fb-01")
    assert fb.verdict == "correct" and fb.earned == 3


def test_fill_blank_accept_alias(assignment):
    r = grade(assignment, {
        "fb-01": FillBlankAnswer(values=("5", "<class 'float'>")),
    })
    fb = next(it for it in r.items if it.qid == "fb-01")
    assert fb.verdict == "correct" and fb.earned == 3


def test_fill_blank_partial(assignment):
    r = grade(assignment, {"fb-01": FillBlankAnswer(values=("5", "int"))})
    fb = next(it for it in r.items if it.qid == "fb-01")
    assert fb.verdict == "partial"
    assert fb.earned == pytest.approx(1.5)      # 3 分两空，对一空


def test_fill_blank_strip(assignment):
    r = grade(assignment, {"fb-01": FillBlankAnswer(values=("  5  ", "float "))})
    fb = next(it for it in r.items if it.qid == "fb-01")
    assert fb.verdict == "correct"


def test_single_choice_wrong(assignment):
    r = grade(assignment, {"sc-01": SingleChoiceAnswer(selected="A")})
    sc = next(it for it in r.items if it.qid == "sc-01")
    assert sc.verdict == "wrong" and sc.earned == 0


def test_unanswered_all_zero_and_flagged(assignment):
    r = grade(assignment, {})
    assert r.auto.earned == 0
    assert all(it.verdict == "unanswered" for it in r.items)
    assert r.manual.earned == 0
    assert r.manual.total == MANUAL_TOTAL


def test_blank_string_counts_as_unanswered(assignment):
    r = grade(assignment, {"sc-01": SingleChoiceAnswer(selected="   ")})
    sc = next(it for it in r.items if it.qid == "sc-01")
    assert sc.verdict == "unanswered"


def test_unknown_qid_ignored(assignment, good_py: Path):
    r = grade(assignment, {"sc-01": SingleChoiceAnswer(selected="C"),
                           "ghost-99": SingleChoiceAnswer(selected="A")})
    assert r.auto.earned == 4


def test_grand_totals(assignment, good_py: Path):
    r = grade(assignment, {
        "sc-01": SingleChoiceAnswer(selected="C"),
        "ce-01": CodeExplainAnswer(text="回答"),
        "pg-01": ProgrammingAnswer(file=str(good_py)),
    })
    assert r.grand_total_points == TOTAL_POINTS
    assert r.grand_total_earned == 4          # 只有已给分的算


# ---------------------------------------------------------------------------
# 手动题流转
# ---------------------------------------------------------------------------


def test_manual_pending_then_graded(assignment, good_py: Path):
    r = grade(assignment, {
        "ce-01": CodeExplainAnswer(text="计算平均值，命名不清晰"),
        "pg-01": ProgrammingAnswer(file=str(good_py)),
    })
    ce = next(it for it in r.items if it.qid == "ce-01")
    pg = next(it for it in r.items if it.qid == "pg-01")
    assert ce.verdict == "pending_manual" and ce.earned is None
    assert pg.verdict == "pending_manual"
    assert pg.parse_result is not None and pg.parse_result.ok
    assert "add" in pg.parse_result.defs

    r2 = apply_manual_score(r, ManualScore(qid="ce-01", score=6, comment="要点基本到位"))
    ce2 = next(it for it in r2.items if it.qid == "ce-01")
    assert ce2.verdict == "graded_manual" and ce2.earned == 6
    assert ce2.detail == "要点基本到位"
    assert r2.manual.earned == 6

    # 原报告不可变
    assert ce.earned is None


def test_programming_syntax_error_recorded(assignment, syntax_err_py: Path):
    r = grade(assignment, {"pg-01": ProgrammingAnswer(file=str(syntax_err_py))})
    pg = next(it for it in r.items if it.qid == "pg-01")
    assert pg.verdict == "pending_manual"          # 语法错也只是提示，仍走人工
    assert pg.parse_result.ok is False
    assert "语法错误" in pg.detail


def test_programming_missing_def_hint(assignment, no_add_py: Path):
    r = grade(assignment, {"pg-01": ProgrammingAnswer(file=str(no_add_py))})
    pg = next(it for it in r.items if it.qid == "pg-01")
    assert pg.parse_result.missing_defs == ("add",)
    assert "add" in pg.detail


# ---------------------------------------------------------------------------
# apply_manual_score 的防呆
# ---------------------------------------------------------------------------


def test_score_unknown_qid(assignment, good_py: Path):
    r = grade(assignment, {"pg-01": ProgrammingAnswer(file=str(good_py))})
    with pytest.raises(KeyError):
        apply_manual_score(r, ManualScore(qid="ghost", score=1))


def test_score_auto_question_rejected(assignment):
    r = grade(assignment, {"sc-01": SingleChoiceAnswer(selected="C")})
    with pytest.raises(ValueError, match="不是手动题"):
        apply_manual_score(r, ManualScore(qid="sc-01", score=4))


def test_score_unanswered_rejected(assignment):
    r = grade(assignment, {})
    with pytest.raises(ValueError, match="未作答"):
        apply_manual_score(r, ManualScore(qid="ce-01", score=5))


def test_score_overflow_rejected(assignment, good_py: Path):
    r = grade(assignment, {"pg-01": ProgrammingAnswer(file=str(good_py))})
    with pytest.raises(ValueError, match="超过"):
        apply_manual_score(r, ManualScore(qid="pg-01", score=7.5))


def test_double_grading_rejected(assignment, good_py: Path):
    r = grade(assignment, {"pg-01": ProgrammingAnswer(file=str(good_py))})
    r2 = apply_manual_score(r, ManualScore(qid="pg-01", score=7))
    with pytest.raises(ValueError, match="不能再给分"):
        apply_manual_score(r2, ManualScore(qid="pg-01", score=3))
