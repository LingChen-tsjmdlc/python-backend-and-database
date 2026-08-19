"""core.parse —— 学员提交的 .py 文件解析（只解析、绝不执行）。

安全边界：
- 只用 ``ast.parse`` 做静态分析，不 import、不 exec、不 eval。
- 只接受 ``.py`` 后缀；文件大小上限 256 KB，超大直接拒绝（防误传大文件）。
"""

from __future__ import annotations

import ast
from pathlib import Path

from .schema import ParseResult

MAX_FILE_BYTES = 256 * 1024


class ParseFileError(Exception):
    """文件本身不可用（不存在 / 非 .py / 过大 / 编码读不了）。"""


def parse_py_file(path: Path, expect_defs: tuple[str, ...] | list[str] = ()) -> ParseResult:
    """解析学员 .py 文件。

    - 语法错误不抛异常，返回 ``ok=False`` + 摘要（学员要能看到错在哪）。
    - 文件不可用（路径/后缀/大小/编码）抛 ParseFileError（调用方的输入错误）。
    """
    path = Path(path)
    expect = tuple(expect_defs)

    if not path.is_file():
        raise ParseFileError(f"文件不存在: {path}")
    if path.suffix.lower() != ".py":
        raise ParseFileError(f"只接受 .py 文件: {path.name}")
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ParseFileError(f"文件过大（{size} 字节 > {MAX_FILE_BYTES}），拒绝解析")

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise ParseFileError(f"不是 UTF-8 文本: {e}") from e
    except OSError as e:
        raise ParseFileError(f"读取失败: {e}") from e

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        return ParseResult(
            ok=False,
            syntax_error=f"第 {e.lineno} 行: {e.msg}",
            defs=(),
            missing_defs=expect,
        )

    defs = tuple(
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )
    missing = tuple(d for d in expect if d not in defs)

    return ParseResult(ok=True, syntax_error=None, defs=defs, missing_defs=missing)


def parse_py_source(source: str, expect_defs: tuple[str, ...] | list[str] = ()) -> ParseResult:
    """解析编辑器直写的代码字符串（同样只解析、不执行）。"""
    expect = tuple(expect_defs)
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return ParseResult(
            ok=False,
            syntax_error=f"第 {e.lineno} 行: {e.msg}",
            defs=(),
            missing_defs=expect,
        )

    defs = tuple(
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )
    missing = tuple(d for d in expect if d not in defs)

    return ParseResult(ok=True, syntax_error=None, defs=defs, missing_defs=missing)
