"""parse 测试：defs 提取、语法错误、expect_defs 缺失、文件级错误。"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.parse import MAX_FILE_BYTES, ParseFileError, parse_py_file


def test_parse_good_file_extracts_defs(good_py: Path):
    r = parse_py_file(good_py, expect_defs=["add"])
    assert r.ok is True
    assert r.syntax_error is None
    assert r.defs == ("add", "Calc")
    assert r.missing_defs == ()


def test_parse_missing_expect_def(no_add_py: Path):
    r = parse_py_file(no_add_py, expect_defs=["add"])
    assert r.ok is True
    assert r.missing_defs == ("add",)


def test_parse_syntax_error_not_raised(syntax_err_py: Path):
    r = parse_py_file(syntax_err_py)
    assert r.ok is False
    assert r.syntax_error is not None and "行" in r.syntax_error
    assert r.defs == ()


def test_parse_empty_expect_passes(no_add_py: Path):
    r = parse_py_file(no_add_py)
    assert r.ok and r.missing_defs == ()


def test_file_not_found(tmp_path: Path):
    with pytest.raises(ParseFileError, match="不存在"):
        parse_py_file(tmp_path / "ghost.py")


def test_reject_non_py_suffix(tmp_path: Path):
    p = tmp_path / "answer.txt"
    p.write_text("print('hi')", encoding="utf-8")
    with pytest.raises(ParseFileError, match=r"\.py"):
        parse_py_file(p)


def test_reject_oversized_file(tmp_path: Path):
    p = tmp_path / "big.py"
    p.write_bytes(b"# pad\n" * (MAX_FILE_BYTES // 6 + 1))
    with pytest.raises(ParseFileError, match="过大"):
        parse_py_file(p)


def test_reject_non_utf8(tmp_path: Path):
    p = tmp_path / "gbk.py"
    p.write_bytes("print('中文')".encode("gbk"))
    with pytest.raises(ParseFileError, match="UTF-8"):
        parse_py_file(p)


def test_async_def_counts(good_py: Path):
    p = good_py.with_name("async_version.py")
    p.write_text("async def main():\n    pass\n", encoding="utf-8")
    r = parse_py_file(p)
    assert r.defs == ("main",)
