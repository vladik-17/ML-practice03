"""Загрузка сохранённых моделей scikit-learn."""

from pathlib import Path

import joblib


def load_model(model_path: str | Path):
    """Проверяет наличие файла и загружает модель."""
    path = Path(model_path)
    # Для отсутствующего артефакта указываем путь в сообщении об ошибке.
    if not path.is_file():
        raise FileNotFoundError(f"Файл модели не найден: {path}")
    return joblib.load(path)
