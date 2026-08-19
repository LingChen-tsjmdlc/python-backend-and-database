"""共享路径与常量（window 与 grade_page 共用，避免循环导入）。"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK_ROOT = ROOT

# 六个部分：目录名 → 展示名
PART_LABELS = {
    "part1_python": "第 1 部分 · Python 基础",
    "part2_database": "第 2 部分 · 数据库（MySQL）",
    "part3_network": "第 3 部分 · 网络通信",
    "part4_flask": "第 4 部分 · Flask 框架",
    "part5_fastapi": "第 5 部分 · FastAPI 框架",
    "part6_engineering": "第 6 部分 · 工程化与实战",
}
