"""core.answers —— 学生答案文件的存/读/更新（纯函数，无界面依赖）。

存储布局（2026-08-19 定）：学生答案与题库同目录，人名学生文件夹隔离——

    homework/part1_python/
    ├── section2.yaml              ← 题库
    └── Jerry/
        └── section2.yaml          ← Jerry 对这份作业的答案

文件内容（无分数口径）：

    version: 1
    assignment: part1-section2
    student: Jerry
    started_at: "2026-08-19T22:30:00"
    updated_at: "2026-08-19T22:45:12"
    status: in_progress            # in_progress | submitted
    answers:
      sc-01: {selected: C}
      fb-01: {values: ["5", "float"]}
      ce-01: {text: "..."}
      pg-01: {source: "..."}
    report:                        # 提交判分后写入（GradeReport dump）
      assignment_id: part1-section2
      items: [...]

答案字典不存题型：恢复时按 qid 查 assignment 得题型，再构造对应 Answer 模型。
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import yaml

from .grader import grade
from .schema import (
    Answer,
    Assignment,
    CodeExplainAnswer,
    FillBlankAnswer,
    GradeReport,
    ManualReview,
    ProgrammingAnswer,
    SingleChoiceAnswer,
)

ANSWERS_VERSION = 1

_ILLEGAL = re.compile(r'[\\/:*?"<>|]')


def sanitize_name(name: str) -> str:
    """Windows 文件夹名清洗：非法字符换 _，去首尾空白。"""
    cleaned = _ILLEGAL.sub("_", name.strip())
    return cleaned or "unnamed"


def student_answers_path(bank_yaml: Path, student: str) -> Path:
    """答案文件 = 题库文件同目录 / <学生名> / <题库同名 .yaml>。"""
    bank_yaml = Path(bank_yaml)
    return bank_yaml.parent / sanitize_name(student) / (bank_yaml.stem + ".yaml")


# ---------------------------------------------------------------------------
# 写
# ---------------------------------------------------------------------------


def save_answers(
    path: Path,
    assignment: Assignment,
    student: str,
    answers: dict[str, Answer],
    status: str = "in_progress",
    report: GradeReport | None = None,
    reviews: dict[str, ManualReview] | None = None,
) -> Path:
    """（重）写学生答案文件。answers 里的未知 qid 丢弃。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # 保留已有 started_at / report（批改界面只改 reviews，别把学生报告冲掉）
    started = datetime.now().isoformat(timespec="seconds")
    prev_report = None
    if path.is_file():
        try:
            prev = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            started = prev.get("started_at") or started
            prev_report = prev.get("report")
        except Exception:
            pass

    payload = {
        "version": ANSWERS_VERSION,
        "assignment": assignment.id,
        "student": student,
        "started_at": started,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "answers": {qid: _dump_answer(a) for qid, a in answers.items()
                    if qid in {q.id for q in assignment.questions}
                    and _has_content(a)},
    }
    final_report = report if report is not None else prev_report
    if final_report is not None:
        # report 参数是 GradeReport 对象；prev_report 已是 dict
        payload["report"] = (final_report.model_dump(mode="json")
                             if not isinstance(final_report, dict) else final_report)
    if reviews:
        payload["reviews"] = {qid: rv.model_dump(mode="json")
                              for qid, rv in reviews.items()
                              if qid in {q.id for q in assignment.questions}}

    path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def _has_content(a: Answer) -> bool:
    """答案有实质内容才落盘：selected/文本/文件/代码 任一非空。"""
    d = a.model_dump(mode="json")
    if isinstance(a, SingleChoiceAnswer):
        return bool((d.get("selected") or "").strip())
    if isinstance(a, CodeExplainAnswer):
        return bool((d.get("text") or "").strip())
    if isinstance(a, ProgrammingAnswer):
        return bool((d.get("file") or "").strip() or (d.get("source") or "").strip())
    if isinstance(a, FillBlankAnswer):
        return any(v is not None and v.strip() for v in d.get("values", ()))
    return True


def _dump_answer(a: Answer) -> dict:
    d = a.model_dump(mode="json")
    return {k: v for k, v in d.items() if v not in (None, "", (), [])}


# ---------------------------------------------------------------------------
# 读
# ---------------------------------------------------------------------------


def load_answers(
    path: Path, assignment: Assignment
) -> tuple[dict[str, Answer], str, GradeReport | None, dict[str, ManualReview]]:
    """读学生答案文件。

    返回 (answers, status, report, reviews)。文件不存在 → 空。
    结构坏 / 题型不匹配的条目跳过（容错：手改文件不拖垮应用）。
    """
    path = Path(path)
    if not path.is_file():
        return {}, "", None, {}

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}, "", None, {}

    if not isinstance(data, dict) or data.get("assignment") != assignment.id:
        return {}, "", None, {}

    raw_answers = data.get("answers") or {}
    answers: dict[str, Answer] = {}
    for qid, raw in raw_answers.items():
        try:
            q = assignment.question(qid)
        except KeyError:
            continue
        if not isinstance(raw, dict):
            continue
        answers[qid] = _build_answer(q.type, raw)

    reviews: dict[str, ManualReview] = {}
    for qid, raw in (data.get("reviews") or {}).items():
        if not isinstance(raw, dict):
            continue
        try:
            reviews[qid] = ManualReview.model_validate(raw)
        except Exception:
            continue

    status = data.get("status") if data.get("status") in ("in_progress", "submitted") else "in_progress"
    report = None
    if data.get("report"):
        try:
            report = GradeReport.model_validate(data["report"])
        except Exception:
            report = None
    return answers, status, report, reviews


_ANSWER_TYPES = {
    "single_choice": SingleChoiceAnswer,
    "fill_blank": FillBlankAnswer,
    "code_explain": CodeExplainAnswer,
    "programming": ProgrammingAnswer,
}


def _build_answer(qtype: str, raw: dict) -> Answer:
    cls = _ANSWER_TYPES[qtype]
    return cls.model_validate(raw)


# ---------------------------------------------------------------------------
# 提交（判分 + 落盘）
# ---------------------------------------------------------------------------


def submit_answers(
    path: Path,
    assignment: Assignment,
    student: str,
    answers: dict[str, Answer],
) -> GradeReport:
    """判分 → status=submitted → 连报告写盘，返回报告。"""
    report = grade(assignment, answers)
    save_answers(path, assignment, student, answers, status="submitted", report=report)
    return report


# ---------------------------------------------------------------------------
# 批改界面辅助
# ---------------------------------------------------------------------------


def list_students(bank_yaml: Path) -> list[str]:
    """某题库下已作答的学生名单（人名文件夹，按字母序）。

    只列出文件夹里存在同名 .yaml 的（有效作答）。
    """
    bank_yaml = Path(bank_yaml)
    if not bank_yaml.parent.is_dir():
        return []
    students = []
    for d in bank_yaml.parent.iterdir():
        if d.is_dir() and (d / (bank_yaml.stem + ".yaml")).is_file():
            students.append(d.name)
    return sorted(students)


def save_review(
    path: Path,
    assignment: Assignment,
    student: str,
    answers: dict[str, Answer],
    status: str,
    review: ManualReview,
) -> Path:
    """写回单条批改记录：读现有 reviews → 合并该条 → 整文件重写。"""
    _, _, _, reviews = load_answers(path, assignment)
    reviews[review.qid] = review
    return save_answers(path, assignment, student, answers,
                        status=status, reviews=reviews)
