"""GUI 冒烟：三页流转 + 四种渲染器（pytest-qt，不进事件循环）。

注：实时保存的 QTimer 防抖依赖事件循环时间推进，CI/offscreen 环境下
定时器事件可能被饿死——这里只测挂载/恢复/直调 flush 的链路。
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PySide6")

# 本文件在 WorkBuddy 执行沙箱内会因 sitecustomize 文件垫片与
# HeroSideUIProvider.setup 的字体加载冲突而 OSError（Bad file descriptor）。
# 开发机（uv run pytest）正常。检测到沙箱垫片时整文件跳过。
import sys as _sys  # noqa: E402

if any("workbuddy" in str(p).lower() or "app.asar" in str(p).lower()
       for p in _sys.path if p):
    pytest.skip("WorkBuddy sandbox detected: GUI tests run on dev machine only",
                allow_module_level=True)

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
STUDENT = "GuiSmoke"


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    HeroSideUIProvider.setup(app, theme="light")
    return app


@pytest.fixture
def win(qtbot, tmp_path):
    """构造主窗口并模拟到作业页（填姓名 → 自动挂载第一份作业）。"""
    w = MainWindow()
    qtbot.addWidget(w)
    w._name_input.set_text(STUDENT)
    w._confirm_name()
    yield w
    import shutil
    for d in (SECTION2.parent / STUDENT,):
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------
# 渲染器（P4）
# ---------------------------------------------------------------------------


def test_renderers_created_for_all_types(qapp):
    a = load_assignment(SECTION2).assignment
    for q in a.questions:
        r = create_renderer(q, theme="light")
        assert r.widget() is not None
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

    r._inputs[0].set_text("  6 ")
    r._inputs[1].set_text("P")
    ans = r.collect()
    assert isinstance(ans, FillBlankAnswer)
    assert ans.values == ("  6 ", "P")       # strip 交给 grader
    assert r.is_answered() is True


def test_programming_starter_is_unanswered(qapp, qtbot):
    """编程题 starter 预填但未改动 → collect 视为未作答。"""
    a = load_assignment(SECTION2).assignment
    q = next(x for x in a.questions if x.id == "pg-01")
    r = create_renderer(q, theme="light")
    qtbot.addWidget(r.widget())

    assert r.collect().source is None        # starter 原样 → None
    assert r.is_answered() is False
    r._editor.set_value("def bmi(w, h):\n    return round(w / h ** 2, 1)\n")
    assert r.collect().source is not None
    assert r.is_answered() is True


# ---------------------------------------------------------------------------
# 三页流转 + 挂载（P3 + 存储）
# ---------------------------------------------------------------------------


def test_three_pages_flow(win):
    assert win._stack.count() == 3
    assert win._stack.currentIndex() == 2          # 姓名确认后到作业页
    assert win._assignment is not None
    assert len(win._renderers) == len(win._assignment.questions) == 17
    assert win._tabs.count() == 4
    assert win._bank_lay.count() >= 7              # 6 部分标题 + 分割线 + 按钮


def test_collect_answers_shape(win):
    win._renderers["sc-01"]._group.set_value("C")
    win._renderers["fb-01"]._inputs[0].set_text("6")
    win._renderers["fb-01"]._inputs[1].set_text("P")

    answers = win.collect_answers()
    assert set(answers.keys()) == {q.id for q in win._assignment.questions}
    assert answers["sc-01"] == SingleChoiceAnswer(selected="C")
    assert isinstance(answers["pg-01"], ProgrammingAnswer)
    assert answers["pg-01"].source is None         # starter 未动 → 未作答


def test_flush_save_and_restore(win):
    """直调 flush（关窗兜底同路径）→ 破坏现场 → 重新挂载恢复。"""
    win._renderers["sc-01"]._group.set_value("C")
    win._renderers["fb-01"]._inputs[0].set_text("6")
    win._flush_save()

    f = win._answers_file
    assert f.is_file(), "答案文件应已落盘"
    assert f.parent.name == STUDENT

    # 破坏现场后重新挂载
    win._renderers["sc-01"]._group.set_value("B")
    win._renderers["fb-01"]._inputs[0].set_text("XX")
    win._on_assignment_picked(win._assignment.id)
    assert win._renderers["sc-01"]._group.value() == "C"
    assert win._renderers["fb-01"]._inputs[0].text() == "6"


def test_submit_locks(win):
    win._renderers["sc-01"]._group.set_value("C")
    win._on_submit()
    assert win._saved_status == "submitted"
    assert not win._submit_btn.isEnabled()
