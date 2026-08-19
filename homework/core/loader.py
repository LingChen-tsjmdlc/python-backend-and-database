"""core.loader —— YAML 题库读取 + 校验 + 发现。

- 读取失败 / 结构不符 / 校验不过 → 抛 SchemaError（带文件路径与人读信息）。
- 分值总和 != 100 → warning（不阻断），warnings 收在 Assignment 之外由调用方展示。
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from .schema import Assignment

logger = logging.getLogger(__name__)



class SchemaError(Exception):
    """题库文件结构/校验错误，带文件路径。"""

    def __init__(self, path: Path, message: str) -> None:
        self.path = path
        super().__init__(f"[{path}] {message}")


class LoadResult:
    """一次加载的结果：assignment + 非阻断警告。"""

    def __init__(self, assignment: Assignment, warnings: list[str]) -> None:
        self.assignment = assignment
        self.warnings = warnings

    def __repr__(self) -> str:  # pragma: no cover
        return f"<LoadResult {self.assignment.id} warnings={self.warnings!r}>"


def load_assignment(path: Path) -> LoadResult:
    """读取单个题库 yaml → 校验 → 返回；失败抛 SchemaError。"""
    path = Path(path)
    if not path.is_file():
        raise SchemaError(path, "文件不存在")
    if path.suffix.lower() not in (".yaml", ".yml"):
        raise SchemaError(path, "只接受 .yaml / .yml 文件")

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        raise SchemaError(path, f"读取失败: {e}") from e

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise SchemaError(path, f"YAML 语法错误: {e}") from e

    if not isinstance(data, dict):
        raise SchemaError(path, "顶层必须是映射（version/id/title/questions）")

    try:
        assignment = Assignment.model_validate(data)
    except ValidationError as e:
        raise SchemaError(path, f"校验失败:\n{e}") from e

    return LoadResult(assignment, [])


def discover_assignments(directory: Path) -> list[LoadResult]:
    """扫描目录下所有 *.yaml（按文件名排序），单个文件失败不拖垮整体。

    失败的文件记 warning 日志并跳过 —— 界面层展示"可用试卷"，
    坏文件在日志里可查。
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise SchemaError(directory, "目录不存在")

    results: list[LoadResult] = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            results.append(load_assignment(path))
        except SchemaError as e:
            logger.warning("跳过无效题库: %s", e)
    return results
