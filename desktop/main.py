"""Запуск приложения и открытие главного окна."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# При прямом запуске добавляем корень проекта для импорта модулей.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from desktop.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # Цикл Qt принимает нажатия и доставляет сигналы от рабочего потока.
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
