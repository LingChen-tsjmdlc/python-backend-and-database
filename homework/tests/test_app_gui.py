"""GUI 冒烟：P3 骨架 + P4 渲染器（pytest-qt，不进事件循环）。"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication  # noqa: E402

from hero_side_ui import HeroSideUIProvider  # noqa: E402

from app.renderers import create_renderer  # noqa: E402
from app.window import MainWindow  # noqa: E402
from core.loader import load_assignment  # noqa: E402
from core.schema import (  # noqa: E402
    FillBlankAnswer,
    ProgrammingAnswer,
    SingleChoiceAnswer,
)

SECTION2 = Path(__file__).resolve().parent.parent / "part1_python" / "section2.yaml"


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    HeroSideUIProvider.setup(app, theme="light")
    return app


# ---------------------------------------------------------------------------
# P4：四种渲染器逐个冒烟
# ---------------------------------------------------------------------------


def test_renderers_created_for_all_types(qapp):
    a = load_assignment(SECTION2).assignment
    for q in a.questions:
        r = create_renderer(q, theme="light")
        w = r.widget()
        assert w is not None
        assert r.collect() is not None
        assert r.is_answered() is False      # 初始未作答


def test_single_choice_collect(qapp, qtbot):
    a = load_assignment(SECTION2).assignment
    q = next(x for x in a.questions if x.id == "sc-01")
    r = create_renderer(q, theme="light")
    qtbot.addWidget(r.widget())

    assert r.collect().selected is None
    r._group.set_value("C")
    assert r.collect().selected == "C"
    assert r.is_answered() is True


def test_fill_blank_collect(qapp, qtbot):
    a = load_assignment(SECTION2).assignment
    q = next(x for x in a.questions if x.id == "fb-01")
    r = create_renderer(q, theme="light")
    qtbot.addWidget(r.widget())

    r._inputs[0].setText("  6 ")
    r._inputs[1].setText("P")
    ans = r.collect()
    assert isinstance(ans, FillBlankAnswer)
    assert ans.values == ("  6 ", "P")       # strip 交给 grader
    assert r.is_answered() is True


def test_programming_pick_flow(qapp, qtbot, tmp_path):
    a = load_assignment(SECTION2).assignment
    q = next(x for x in a.questions if x.id == "pg-01")
    r = create_renderer(q, theme="light")
    qtbot.addWidget(r.widget())

    assert r.collect().file is None
    f = tmp_path / "answer.py"
    f.write_text("def bmi(w, h):\n    return round(w / h ** 2, 1)\n", encoding="utf-8")
    r._file = f                                    # 绕过对话框，直接注入
    assert r.collect().file == str(f)
    assert r.is_answered() is True


# ---------------------------------------------------------------------------
# P3：主窗口骨架
# ---------------------------------------------------------------------------


def test_main_window_builds_and_loads(qapp, qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    assert win._listbox is not None
    assert win._assignment is not None, "应自动选中第一个章节"
    assert len(win._renderers) == len(win._assignment.questions) == 17

    # 题卡数 == 题目数
    cards = [w for w in win._cards_host.findChildren(type(win)) if isinstance(w, type(win._cards_host))]
    assert win._cards_lay.count() >= 17


def test_collect_answers_shape(qapp, qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    # 模拟作答两题
    win._renderers["sc-01"]._group.set_value("C")
    win._renderers["fb-01"]._inputs[0].setText("6")
    win._renderers["fb-01"]._inputs[1].setText("P")

    answers = win.collect_answers()
    assert set(answers.keys()) == {q.id for q in win._assignment.questions}
    assert answers["sc-01"] == SingleChoiceAnswer(selected="C")
    assert isinstance(answers["pg-01"], ProgrammingAnswer)
    assert answers["pg-01"].file is None                        # 未选文件

    win._update_progress()
    answered = sum(1 for r in win._renderers.values() if r.is_answered())
    assert answered == 2                                        # sc-01 + fb-01
