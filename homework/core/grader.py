"""core.grader —— 纯函数判分（无分数：自动题判对错，手动题流转批阅状态）。"""

from __future__ import annotations

from pathlib import Path

from .parse import parse_py_file, parse_py_source
from .schema import (
    AUTO_TYPES,
    MANUAL_TYPES,
    Answer,
    Assignment,
    CodeExplain,
    CodeExplainAnswer,
    FillBlank,
    FillBlankAnswer,
    GradeReport,
    ItemResult,
    ManualReview,
    Programming,
    ProgrammingAnswer,
    SingleChoice,
    SingleChoiceAnswer,
)


# ---------------------------------------------------------------------------
# 单题判分
# ---------------------------------------------------------------------------


def _grade_single_choice(q: SingleChoice, a: SingleChoiceAnswer | None) -> ItemResult:
    if a is None or not (a.selected or "").strip():
        return ItemResult(qid=q.id, qtype=q.type, verdict="unanswered", detail="未选择")
    selected = a.selected.strip()
    correct = selected == q.answer
    return ItemResult(
        qid=q.id, qtype=q.type,
        verdict="correct" if correct else "wrong",
        detail=f"选 {selected}，正确答案 {q.answer}",
    )


def _norm(v: str | None) -> str:
    return (v or "").strip()


def _grade_fill_blank(q: FillBlank, a: FillBlankAnswer | None) -> ItemResult:
    if a is None or not a.values or all(v is None or not _norm(v) for v in a.values):
        return ItemResult(qid=q.id, qtype=q.type, verdict="unanswered", detail="未填写")

    n_correct = 0
    details: list[str] = []

    for i, blank in enumerate(q.blanks):
        given = _norm(a.values[i]) if i < len(a.values) else ""
        expected = blank.answer.strip()
        accepts = {_norm(x) for x in blank.accept}
        hit = given == expected or (given and given in accepts)
        if hit:
            n_correct += 1
            details.append(f"空{i + 1} 对")
        else:
            details.append(f"空{i + 1} 错（填 {given!r}，应 {expected!r}）")

    if n_correct == len(q.blanks):
        verdict, note = "correct", ""
    elif n_correct == 0:
        verdict, note = "wrong", ""
    else:
        verdict, note = "partial", f"，对 {n_correct}/{len(q.blanks)} 空"
    return ItemResult(
        qid=q.id, qtype=q.type, verdict=verdict,
        detail="；".join(details) + note,
    )


def _grade_code_explain(q: CodeExplain, a: CodeExplainAnswer | None) -> ItemResult:
    if a is None or not _norm(a.text):
        return ItemResult(qid=q.id, qtype=q.type, verdict="unanswered", detail="未作答")
    return ItemResult(qid=q.id, qtype=q.type, verdict="pending_manual", detail="等待人工批阅")


def _grade_programming(q: Programming, a: ProgrammingAnswer | None) -> ItemResult:
    if a is None or (not _norm(a.file) and not _norm(a.source)):
        return ItemResult(qid=q.id, qtype=q.type, verdict="unanswered", detail="未作答")

    # 二选一来源：编辑器直写（source）或选文件（file）
    if _norm(a.source):
        parse_result = parse_py_source(a.source, q.expect_defs)
    else:
        parse_result = parse_py_file(Path(a.file), q.expect_defs)  # type: ignore[arg-type]

    hint: str
    if not parse_result.ok:
        hint = f"语法错误：{parse_result.syntax_error}"
    elif parse_result.missing_defs:
        hint = f"缺少预期定义: {', '.join(parse_result.missing_defs)}"
    else:
        hint = f"解析通过，定义: {', '.join(parse_result.defs) or '（无顶层定义）'}"
    return ItemResult(qid=q.id, qtype=q.type, verdict="pending_manual",
                      parse_result=parse_result, detail=hint)


# ---------------------------------------------------------------------------
# 整卷判分
# ---------------------------------------------------------------------------


def grade(assignment: Assignment, answers: dict[str, Answer]) -> GradeReport:
    """对整份卷子判分。answers 的 key 是 qid；未知 qid 忽略，缺失视为未作答。"""
    items: list[ItemResult] = []

    for q in assignment.questions:
        a = answers.get(q.id)
        if q.type == "single_choice":
            assert isinstance(q, SingleChoice) and (a is None or isinstance(a, SingleChoiceAnswer))
            items.append(_grade_single_choice(q, a))
        elif q.type == "fill_blank":
            assert isinstance(q, FillBlank) and (a is None or isinstance(a, FillBlankAnswer))
            items.append(_grade_fill_blank(q, a))
        elif q.type == "code_explain":
            assert isinstance(q, CodeExplain) and (a is None or isinstance(a, CodeExplainAnswer))
            items.append(_grade_code_explain(q, a))
        elif q.type == "programming":
            assert isinstance(q, Programming) and (a is None or isinstance(a, ProgrammingAnswer))
            items.append(_grade_programming(q, a))
        else:  # pragma: no cover - schema 已限制 type
            raise ValueError(f"未知题型 {q.type}")

    return GradeReport(assignment_id=assignment.id, items=tuple(items))


# ---------------------------------------------------------------------------
# 人工批阅写回
# ---------------------------------------------------------------------------


def apply_manual_review(report: GradeReport, review: ManualReview) -> GradeReport:
    """把一道手动题的批阅结论写回，返回新报告（原报告不变）。

    - 只接受 pending_manual 的题；unanswered 不允许批阅。
    """
    target = next((it for it in report.items if it.qid == review.qid), None)
    if target is None:
        raise KeyError(f"报告中不存在题目 {review.qid}")
    if target.qtype not in MANUAL_TYPES:
        raise ValueError(f"{review.qid} 是 {target.qtype}，不是手动题")
    if target.verdict == "unanswered":
        raise ValueError(f"{review.qid} 未作答，不能批阅")
    if target.verdict != "pending_manual":
        raise ValueError(f"{review.qid} 当前状态 {target.verdict}，不能再批阅")

    new_items = tuple(
        it.model_copy(update={
            "verdict": "graded_manual",
            "passed": review.passed,
            "detail": (review.comment or "").strip() or it.detail,
        })
        if it.qid == review.qid else it
        for it in report.items
    )
    return report.model_copy(update={"items": new_items})
