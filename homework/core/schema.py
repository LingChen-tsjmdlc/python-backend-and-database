"""core.schema —— pydantic 模型：题目 / 试卷 / 答案 / 判分报告。

约定：
- 判别字段是 ``type``，取值 ``single_choice`` / ``fill_blank`` / ``code_explain`` / ``programming``。
- "代码分析题"不是独立题型，是带 ``code`` 字段的 ``single_choice``。
- 所有模型 frozen（不可变），判分过程中不会被界面层意外改动。
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class _Model(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# ---------------------------------------------------------------------------
# 题目
# ---------------------------------------------------------------------------


class Option(_Model):
    key: str
    text: str


class _QuestionBase(_Model):
    id: str = Field(min_length=1)
    points: int = Field(gt=0)
    stem: str = Field(min_length=1)
    code: str | None = None          # 代码上下文，任何题型都可以挂
    explanation: str | None = None
    tags: tuple[str, ...] = ()

    @field_validator("id")
    @classmethod
    def _strip_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("id 不能为空白")
        return v


class SingleChoice(_QuestionBase):
    type: Literal["single_choice"]
    options: tuple[Option, ...] = Field(min_length=2)
    answer: str

    @model_validator(mode="after")
    def _answer_in_options(self) -> "SingleChoice":
        keys = [o.key for o in self.options]
        if len(set(keys)) != len(keys):
            raise ValueError("选项 key 重复")
        if self.answer not in keys:
            raise ValueError(f"answer={self.answer!r} 不在选项 key 中 {keys}")
        return self


class Blank(_Model):
    answer: str
    accept: tuple[str, ...] = ()     # 可选：任一命中即对（同样先 strip）


class FillBlank(_QuestionBase):
    type: Literal["fill_blank"]
    blanks: tuple[Blank, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _blank_answers_not_blank(self) -> "FillBlank":
        for i, b in enumerate(self.blanks):
            if not b.answer.strip():
                raise ValueError(f"第 {i + 1} 空的 answer 不能为空白")
        return self


class CodeExplain(_QuestionBase):
    type: Literal["code_explain"]
    rubric: tuple[str, ...] = Field(min_length=1)   # 批改参考要点
    reference: str | None = None                    # 示范回答，提交后展示

    @field_validator("rubric")
    @classmethod
    def _rubric_items_not_blank(cls, v: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item.strip() for item in v):
            raise ValueError("rubric 要点不能为空白")
        return v


class Programming(_QuestionBase):
    type: Literal["programming"]
    starter: str | None = None
    reference: str | None = None
    expect_defs: tuple[str, ...] = ()               # AST 检查必须出现的函数/类名
    checklist: tuple[str, ...] = ()                 # 人工批改自查清单
    grading: Literal["manual", "self", "tests"] = "manual"


Question = Annotated[
    Union[SingleChoice, FillBlank, CodeExplain, Programming],
    Field(discriminator="type"),
]


# ---------------------------------------------------------------------------
# 试卷
# ---------------------------------------------------------------------------


class Assignment(_Model):
    version: int
    id: str = Field(min_length=1)
    title: str
    questions: tuple[Question, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique_qids(self) -> "Assignment":
        qids = [q.id for q in self.questions]
        dupes = sorted({q for q in qids if qids.count(q) > 1})
        if dupes:
            raise ValueError(f"题目 id 重复: {dupes}")
        return self

    @property
    def total_points(self) -> int:
        return sum(q.points for q in self.questions)

    def question(self, qid: str) -> Question:
        for q in self.questions:
            if q.id == qid:
                return q
        raise KeyError(qid)


# ---------------------------------------------------------------------------
# 学员作答（界面层收集后交给 core）
# ---------------------------------------------------------------------------


class SingleChoiceAnswer(_Model):
    selected: str | None = None


class FillBlankAnswer(_Model):
    values: tuple[str | None, ...] = ()   # 与 blanks 一一对应；None=该空未填


class CodeExplainAnswer(_Model):
    text: str | None = None


class ProgrammingAnswer(_Model):
    file: str | None = None               # .py 文件路径；None=未选文件


Answer = Union[SingleChoiceAnswer, FillBlankAnswer, CodeExplainAnswer, ProgrammingAnswer]


# ---------------------------------------------------------------------------
# 判分报告
# ---------------------------------------------------------------------------

Verdict = Literal[
    "correct",          # 自动题：全对
    "wrong",            # 自动题：错
    "partial",          # 自动题：多空部分对
    "unanswered",       # 未作答（自动题计 0；手动题待批改但没有作答内容）
    "pending_manual",   # 手动题已作答，等人工给分
    "graded_manual",    # 手动题已人工给分
]


class SectionStat(_Model):
    """一段（auto 或 manual）的得分统计。"""

    earned: float
    total: float


class ParseResult(_Model):
    """programming 题学员 .py 文件的 AST 解析结果（只解析、不执行）。"""

    ok: bool                             # 语法是否合法
    syntax_error: str | None = None      # 语法错误摘要（ok=False 时有值）
    defs: tuple[str, ...] = ()           # 顶层函数与类名，按出现顺序
    missing_defs: tuple[str, ...] = ()   # expect_defs 中缺失的


class ItemResult(_Model):
    qid: str
    qtype: str
    points: float
    earned: float | None = None          # None = 尚未得到分数（pending_manual）
    verdict: Verdict
    detail: str | None = None            # 人读的判分说明
    parse_result: ParseResult | None = None   # 仅 programming 题有


class GradeReport(_Model):
    assignment_id: str
    auto: SectionStat                    # 自动判分段（单选 + 填空）
    manual: SectionStat                  # 手动段（解析 + 编程）
    items: tuple[ItemResult, ...]

    @property
    def grand_total_earned(self) -> float:
        """已确认的总得分（auto + 已给分的 manual）。"""
        return self.auto.earned + self.manual.earned

    @property
    def grand_total_points(self) -> float:
        return self.auto.total + self.manual.total


# ---------------------------------------------------------------------------
# 人工给分（手动批改入口，写回报告）
# ---------------------------------------------------------------------------


class ManualScore(_Model):
    qid: str
    score: float = Field(ge=0)
    comment: str | None = None
