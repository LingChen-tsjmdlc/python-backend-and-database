"""app.main —— 入口：QApplication + HeroSideUIProvider + 主窗口。"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from hero_side_ui import HeroSideUIProvider

from .window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    HeroSideUIProvider.setup(
        app,
        theme="light",
        font_family="Microsoft YaHei",
        font_base_size=14,
    )
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
