"""共享 fixture：一个最小但覆盖全部题型的题库 + 学员 py 文件。"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ASSIGNMENT_DICT: dict = {
    "version": 1,
    "id": "test-assignment",
    "title": "测试卷",
    "questions": [
        {
            "id": "sc-01",
            "type": "single_choice",
            "points": 4,
            "stem": "下列哪个是合法的变量名？",
            "options": [
                {"key": "A", "text": "2nd_place"},
                {"key": "B", "text": "player-score"},
                {"key": "C", "text": "player_score"},
                {"key": "D", "text": "class"},
            ],
            "answer": "C",
            "explanation": "标识符不能以数字开头、不能含连字符、class 是关键字。",
        },
        {
            "id": "ca-01",          # 代码分析题 = single_choice + code
            "type": "single_choice",
            "points": 4,
            "code": "a = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)",
            "stem": "上述代码的输出是？",
            "options": [
                {"key": "A", "text": "[1, 2, 3]"},
                {"key": "B", "text": "[1, 2, 3, 4]"},
                {"key": "C", "text": "抛出异常"},
            ],
            "answer": "B",
            "explanation": "b = a 是引用赋值。",
        },
        {
            "id": "fb-01",
            "type": "fill_blank",
            "points": 3,
            "stem": 'len("hello") 是 ____，type(1 + 1.0) 是 ____。',
            "blanks": [
                {"answer": "5"},
                {"answer": "float", "accept": ["<class 'float'>"]},
            ],
            "explanation": "len 返回字符数；int+float 是 float。",
        },
        {
            "id": "ce-01",
            "type": "code_explain",
            "points": 8,
            "code": "total = 0\nfor i in range(10):\n    total = total + i\nprint(total / 10)",
            "stem": "解释这段代码的作用，并指出可能的问题。",
            "rubric": ["说出计算平均值", "指出命名不清晰"],
            "reference": "计算 0~9 的平均值并打印 4.5。",
        },
        {
            "id": "pg-01",
            "type": "programming",
            "points": 7,
            "stem": "编写函数 add(a, b) 返回两数之和。",
            "starter": "def add(a: int, b: int) -> int:\n    ...",
            "reference": "def add(a: int, b: int) -> int:\n    return a + b",
            "expect_defs": ["add"],
            "checklist": ["函数名正确", "返回 a + b"],
            "grading": "manual",
        },
    ],
}

TOTAL_POINTS = 26   # 4 + 4 + 3 + 8 + 7
AUTO_TOTAL = 11     # 4 + 4 + 3
MANUAL_TOTAL = 15   # 8 + 7


@pytest.fixture
def assignment_dict() -> dict:
    return ASSIGNMENT_DICT


@pytest.fixture
def assignment_yaml(tmp_path: Path) -> Path:
    p = tmp_path / "test_assignment.yaml"
    p.write_text(yaml.safe_dump(ASSIGNMENT_DICT, allow_unicode=True), encoding="utf-8")
    return p


GOOD_PY = "def add(a, b):\n    return a + b\n\n\nclass Calc:\n    pass\n"
SYNTAX_ERR_PY = "def add(a, b)\n    return a + b\n"     # 缺冒号
NO_ADD_PY = "def sub(a, b):\n    return a - b\n"


@pytest.fixture
def good_py(tmp_path: Path) -> Path:
    p = tmp_path / "answer_good.py"
    p.write_text(GOOD_PY, encoding="utf-8")
    return p


@pytest.fixture
def syntax_err_py(tmp_path: Path) -> Path:
    p = tmp_path / "answer_syntax.py"
    p.write_text(SYNTAX_ERR_PY, encoding="utf-8")
    return p


@pytest.fixture
def no_add_py(tmp_path: Path) -> Path:
    p = tmp_path / "answer_no_add.py"
    p.write_text(NO_ADD_PY, encoding="utf-8")
    return p
