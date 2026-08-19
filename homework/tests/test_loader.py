"""loader 测试：好数据通过、坏数据拒绝、目录发现（无分数口径）。"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from core.loader import SchemaError, discover_assignments, load_assignment

from .conftest import ASSIGNMENT_DICT


def _write(tmp_path: Path, name: str, data: object) -> Path:
    p = tmp_path / name
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# 正常加载
# ---------------------------------------------------------------------------


def test_load_ok(assignment_yaml: Path):
    result = load_assignment(assignment_yaml)
    a = result.assignment
    assert a.id == "test-assignment"
    assert len(a.questions) == 5
    assert result.warnings == []


def test_points_field_now_rejected(tmp_path: Path):
    """无分数口径：题库带 points 字段应被 extra=forbid 拒绝。"""
    data = copy.deepcopy(ASSIGNMENT_DICT)
    data["questions"][0]["points"] = 4
    with pytest.raises(SchemaError, match="校验失败"):
        load_assignment(_write(tmp_path, "with_points.yaml", data))


# ---------------------------------------------------------------------------
# 坏数据逐一拒绝
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mutate, expect_frag", [
    (lambda d: d["questions"][0].pop("answer"), "answer"),                  # 单选缺 answer
    (lambda d: d["questions"][0].__setitem__("answer", "E"), "不在选项"),    # answer 不在选项
    (lambda d: d["questions"][0].__setitem__("type", "multi_choice"), "multi_choice"),  # 未知 type
    (lambda d: d["questions"][2]["blanks"][0].__setitem__("answer", "  "), "空白"),     # 填空答案是空白
    (lambda d: d["questions"][2].pop("blanks"), "blanks"),                  # 填空缺 blanks
    (lambda d: d["questions"][3].pop("rubric"), "rubric"),                  # code_explain 缺 rubric
    (lambda d: d["questions"][1].__setitem__("id", "sc-01"), "重复"),       # id 重复
    (lambda d: d.pop("title"), "title"),                                    # 缺 title
])
def test_bad_data_rejected(tmp_path: Path, mutate, expect_frag):
    data = copy.deepcopy(ASSIGNMENT_DICT)
    mutate(data)
    with pytest.raises(SchemaError) as ei:
        load_assignment(_write(tmp_path, "bad.yaml", data))
    assert expect_frag in str(ei.value)


def test_not_a_file(tmp_path: Path):
    with pytest.raises(SchemaError, match="文件不存在"):
        load_assignment(tmp_path / "nope.yaml")


def test_wrong_suffix(tmp_path: Path):
    p = tmp_path / "bank.json"
    p.write_text("{}", encoding="utf-8")
    with pytest.raises(SchemaError, match="yaml"):
        load_assignment(p)


def test_yaml_syntax_error(tmp_path: Path):
    p = tmp_path / "broken.yaml"
    p.write_text("questions: [unclosed", encoding="utf-8")
    with pytest.raises(SchemaError, match="YAML"):
        load_assignment(p)


def test_top_level_not_mapping(tmp_path: Path):
    p = tmp_path / "list.yaml"
    p.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(SchemaError, match="顶层"):
        load_assignment(p)


# ---------------------------------------------------------------------------
# 目录发现
# ---------------------------------------------------------------------------


def test_discover_skips_bad_files(tmp_path: Path, assignment_yaml: Path):
    _write(tmp_path, "a_broken.yaml", {"version": 1})       # 结构残缺
    (tmp_path / "notes.txt").write_text("不是题库", encoding="utf-8")  # 非 yaml 不扫
    results = discover_assignments(tmp_path)
    assert [r.assignment.id for r in results] == ["test-assignment"]


def test_discover_sorted_by_filename(tmp_path: Path):
    for name, qid in (("b.yaml", "b-1"), ("a.yaml", "a-1")):
        data = copy.deepcopy(ASSIGNMENT_DICT)
        data["id"] = qid
        _write(tmp_path, name, data)
    results = discover_assignments(tmp_path)
    assert [r.assignment.id for r in results] == ["a-1", "b-1"]


def test_discover_skips_student_answer_dirs(tmp_path: Path, assignment_yaml: Path):
    """学生答案目录（人名文件夹）里的 yaml 不应被当成题库。"""
    (tmp_path / "Jerry").mkdir()
    (tmp_path / "Jerry" / "test_assignment.yaml").write_text(
        "student: Jerry\nanswers: {}", encoding="utf-8"
    )
    results = discover_assignments(tmp_path)
    assert [r.assignment.id for r in results] == ["test-assignment"]


def test_discover_missing_dir(tmp_path: Path):
    with pytest.raises(SchemaError, match="目录不存在"):
        discover_assignments(tmp_path / "ghost")
