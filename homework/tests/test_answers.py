"""answers 存储测试：路径规则、存/读往返、续做保留 started_at、提交流转。"""

from __future__ import annotations

from pathlib import Path

from core.answers import (
    list_students,
    load_answers,
    sanitize_name,
    save_answers,
    student_answers_path,
    submit_answers,
)
from core.loader import load_assignment
from core.schema import (
    CodeExplainAnswer,
    FillBlankAnswer,
    ProgrammingAnswer,
    SingleChoiceAnswer,
)

from .conftest import ASSIGNMENT_DICT

import yaml


def _bank(tmp_path: Path) -> Path:
    p = tmp_path / "section2.yaml"
    p.write_text(yaml.safe_dump(ASSIGNMENT_DICT, allow_unicode=True), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# 路径与清洗
# ---------------------------------------------------------------------------


def test_path_layout(tmp_path: Path):
    bank = tmp_path / "section2.yaml"
    p = student_answers_path(bank, "Jerry")
    assert p == tmp_path / "Jerry" / "section2.yaml"


def test_sanitize_name():
    assert sanitize_name("Jerry") == "Jerry"
    assert sanitize_name('a/b\\c:d*e?f"g<h>i|j') == "a_b_c_d_e_f_g_h_i_j"
    assert sanitize_name("   ") == "unnamed"


# ---------------------------------------------------------------------------
# 存 / 读往返
# ---------------------------------------------------------------------------


def test_save_load_roundtrip(tmp_path: Path):
    bank = _bank(tmp_path)
    a = load_assignment(bank).assignment

    answers = {
        "sc-01": SingleChoiceAnswer(selected="C"),
        "fb-01": FillBlankAnswer(values=("5", "float")),
        "ce-01": CodeExplainAnswer(text="解释"),
        "pg-01": ProgrammingAnswer(source="def add(a, b):\n    return a + b\n"),
    }
    p = student_answers_path(bank, "Jerry")
    save_answers(p, a, "Jerry", answers)

    assert p.is_file()
    loaded, status, report, _reviews = load_answers(p, a)
    assert status == "in_progress"
    assert report is None
    assert loaded["sc-01"] == answers["sc-01"]
    assert loaded["fb-01"] == FillBlankAnswer(values=("5", "float"))
    assert loaded["ce-01"].text == "解释"
    assert "def add" in loaded["pg-01"].source


def test_started_at_preserved_on_resave(tmp_path: Path):
    bank = _bank(tmp_path)
    a = load_assignment(bank).assignment
    p = student_answers_path(bank, "Jerry")

    save_answers(p, a, "Jerry", {"sc-01": SingleChoiceAnswer(selected="C")})
    first = yaml.safe_load(p.read_text(encoding="utf-8"))["started_at"]

    save_answers(p, a, "Jerry", {"sc-01": SingleChoiceAnswer(selected="B")})
    second = yaml.safe_load(p.read_text(encoding="utf-8"))["started_at"]
    assert first == second                       # 续做不重置开始时间


def test_empty_answers_not_dumped(tmp_path: Path):
    bank = _bank(tmp_path)
    a = load_assignment(bank).assignment
    p = student_answers_path(bank, "Jerry")
    save_answers(p, a, "Jerry", {"sc-01": SingleChoiceAnswer(selected=None)})
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert data["answers"] == {}                 # 空选择不落盘


def test_load_missing_file_returns_empty(tmp_path: Path):
    bank = _bank(tmp_path)
    a = load_assignment(bank).assignment
    loaded, status, report, _r = load_answers(bank.parent / "Ghost" / "section2.yaml", a)
    assert loaded == {} and status == "" and report is None


def test_load_tolerates_garbage(tmp_path: Path):
    bank = _bank(tmp_path)
    a = load_assignment(bank).assignment
    p = student_answers_path(bank, "Jerry")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("answers: [broken", encoding="utf-8")     # 坏 yaml
    loaded, status, _st, _rv = load_answers(p, a)
    assert loaded == {} and status == ""


def test_load_skips_mismatched_assignment(tmp_path: Path):
    bank = _bank(tmp_path)
    a = load_assignment(bank).assignment
    p = student_answers_path(bank, "Jerry")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump({"assignment": "other-paper", "answers": {"sc-01": {"selected": "C"}}}),
                 encoding="utf-8")
    loaded, _st, _rp, _rv = load_answers(p, a)
    assert loaded == {}


# ---------------------------------------------------------------------------
# 提交
# ---------------------------------------------------------------------------


def test_submit_writes_report_and_status(tmp_path: Path):
    bank = _bank(tmp_path)
    a = load_assignment(bank).assignment
    p = student_answers_path(bank, "Jerry")

    answers = {
        "sc-01": SingleChoiceAnswer(selected="C"),
        "ca-01": SingleChoiceAnswer(selected="B"),
        "fb-01": FillBlankAnswer(values=("5", "float")),
        "ce-01": CodeExplainAnswer(text="解释"),
        "pg-01": ProgrammingAnswer(source="def add(a, b):\n    return a + b\n"),
    }
    report = submit_answers(p, a, "Jerry", answers)

    assert report.auto_correct == 3 and report.auto_total == 3
    assert report.manual_pending == 2

    loaded, status, loaded_report, _rv = load_answers(p, a)
    assert status == "submitted"
    assert loaded_report is not None
    assert loaded_report.auto_correct == 3


# ---------------------------------------------------------------------------
# 批改记录
# ---------------------------------------------------------------------------


def test_save_and_load_review(tmp_path: Path):
    from core.answers import save_review
    from core.schema import ManualReview, CorrectAnswer
    bank = _bank(tmp_path)
    a = load_assignment(bank).assignment
    p = student_answers_path(bank, "Jerry")

    answers = {"sc-01": SingleChoiceAnswer(selected="A")}
    report = submit_answers(p, a, "Jerry", answers)   # 先提交（带 report）

    # 批错 + 给正确答案
    save_review(p, a, "Jerry", answers, "submitted",
                ManualReview(qid="sc-01", passed=False, comment="看错选项",
                             correct=CorrectAnswer(selected="C")))

    loaded, status, rep, reviews = load_answers(p, a)
    assert status == "submitted"
    assert "sc-01" in reviews
    rv = reviews["sc-01"]
    assert rv.passed is False
    assert rv.correct.selected == "C"
    # 学生 report 未被批改写回冲掉
    assert rep is not None and rep.auto_total == 3


def test_list_students(tmp_path: Path):
    bank = _bank(tmp_path)
    a = load_assignment(bank).assignment
    for name in ("Bob", "Alice"):
        save_answers(student_answers_path(bank, name), a, name, {})
    (tmp_path / "EmptyGuy").mkdir()                    # 无 yaml → 不列
    assert list_students(bank) == ["Alice", "Bob"]
