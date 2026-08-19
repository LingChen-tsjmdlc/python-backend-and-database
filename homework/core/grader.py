"""core.grader —— 纯函数判分。

- 自动题（single_choice / fill_blank）：提交即判。
- 手动题（code_explain / programming）：作答了 → pending_manual；未作答 → unanswered。
- ``apply_manual_score`` 把人工给分写回报告（产生新报告，不就地改）。
"""

from __future__ import annotations

from pathlib import Path

from .parse import parse_py_file
from .schema import (
    Answer,
    Assignment,
    CodeExplain,
    CodeExplainAnswer,
    FillBlank,
    FillBlankAnswer,
    GradeReport,
    ItemResult,
    ManualScore,
    Programming,
    ProgrammingAnswer,
    SectionStat,
    SingleChoice,
    SingleChoiceAnswer,
)

AUTO_TYPES = ("single_choice", "fill_blank")
MANUAL_TYPES = ("code_explain", "programming")


# ---------------------------------------------------------------------------
# 单题判分
# ---------------------------------------------------------------------------


def _grade_single_choice(q: SingleChoice, a: SingleChoiceAnswer | None) -> ItemResult:
    if a is None or a.selected is None:
        return ItemResult(qid=q.id, qtype=q.type, points=q.points, verdict="unanswered",
                          detail="未选择")
    selected = a.selected.strip()
    if not selected:
        return ItemResult(qid=q.id, qtype=q.type, points=q.points, verdict="unanswered",
                          detail="未选择")
    correct = selected == q.answer
    return ItemResult(
        qid=q.id, qtype=q.type, points=q.points,
        earned=q.points if correct else 0.0,
        verdict="correct" if correct else "wrong",
        detail=f"选 {selected}，正确答案 {q.answer}",
    )


def _norm(v: str | None) -> str:
    return (v or "").strip()


def _grade_fill_blank(q: FillBlank, a: FillBlankAnswer | None) -> ItemResult:
    if a is None or not a.values or all(v is None or not _norm(v) for v in a.values):
        return ItemResult(qid=q.id, qtype=q.type, points=q.points, verdict="unanswered",
                          detail="未填写")

    per_blank = q.points / len(q.blanks)          # 多空均分
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

    earned = round(per_blank * n_correct, 2)
    if n_correct == len(q.blanks):
        verdict, note = "correct", ""
    elif n_correct == 0:
        verdict, note = "wrong", ""
    else:
        verdict, note = "partial", f"，对 {n_correct}/{len(q.blanks)} 空"
    return ItemResult(
        qid=q.id, qtype=q.type, points=q.points,
        earned=earned, verdict=verdict,
        detail="；".join(details) + note,
    )


def _grade_code_explain(q: CodeExplain, a: CodeExplainAnswer | None) -> ItemResult:
    if a is None or not _norm(a.text):
        return ItemResult(qid=q.id, qtype=q.type, points=q.points, verdict="unanswered",
                          detail="未作答")
    return ItemResult(qid=q.id, qtype=q.type, points=q.points, earned=None,
                      verdict="pending_manual", detail="等待人工批改")


def _grade_programming(q: Programming, a: ProgrammingAnswer | None) -> ItemResult:
    if a is None or not _norm(a.file):
        return ItemResult(qid=q.id, qtype=q.type, points=q.points, verdict="unanswered",
                          detail="未选择文件")

    parse_result = parse_py_file(Path(a.file), q.expect_defs)
    hint: str
    if not parse_result.ok:
        hint = f"语法错误：{parse_result.syntax_error}"
    elif parse_result.missing_defs:
        hint = f"缺少预期定义: {', '.join(parse_result.missing_defs)}"
    else:
        hint = f"解析通过，定义: {', '.join(parse_result.defs) or '（无顶层定义）'}"
    return ItemResult(qid=q.id, qtype=q.type, points=q.points, earned=None,
                      verdict="pending_manual", parse_result=parse_result, detail=hint)


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

    def _stat(types: tuple[str, ...], only_scored: bool) -> SectionStat:
        pts = earned = 0.0
        for it in items:
            if it.qtype not in types:
                continue
            pts += it.points
            if only_scored and it.earned is not None:
                earned += it.earned
        return SectionStat(earned=round(earned, 2), total=pts)

    auto = _stat(AUTO_TYPES, only_scored=True)
    manual = _stat(MANUAL_TYPES, only_scored=False)   # manual.earned 只含已给分部分
    return GradeReport(
        assignment_id=assignment.id,
        auto=auto,
        manual=manual,
        items=tuple(items),
    )


# ---------------------------------------------------------------------------
# 人工给分写回
# ---------------------------------------------------------------------------


def apply_manual_score(report: GradeReport, score: ManualScore) -> GradeReport:
    """把一道手动题的给分写回，返回新报告（原报告不变）。

    - 只接受 pending_manual 的题；unanswered 不允许给分（防止给未作答题塞分）。
    - 分数 > 题目分值 → ValueError。
    """
    target = next((it for it in report.items if it.qid == score.qid), None)
    if target is None:
        raise KeyError(f"报告中不存在题目 {score.qid}")
    if target.qtype not in MANUAL_TYPES:
        raise ValueError(f"{score.qid} 是 {target.qtype}，不是手动题")
    if target.verdict == "unanswered":
        raise ValueError(f"{score.qid} 未作答，不能给分")
    if target.verdict != "pending_manual":
        raise ValueError(f"{score.qid} 当前状态 {target.verdict}，不能再给分")
    if score.score > target.points:
        raise ValueError(f"给分 {score.score} 超过题目分值 {target.points}")

    new_items = tuple(
        it.model_copy(update={
            "earned": score.score,
            "verdict": "graded_manual",
            "detail": (score.comment or "").strip() or it.detail,
        })
        if it.qid == score.qid else it
        for it in report.items
    )

    manual_earned = round(sum(
        it.earned for it in new_items
        if it.qtype in MANUAL_TYPES and it.earned is not None
    ), 2)
    manual_total = sum(it.points for it in new_items if it.qtype in MANUAL_TYPES)

    return report.model_copy(update={
        "items": new_items,
        "manual": SectionStat(earned=manual_earned, total=manual_total),
    })
