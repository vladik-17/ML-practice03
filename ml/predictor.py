"""Изолированный модуль расчёта прогноза."""

from pathlib import Path
from typing import Any

import numpy as np

from ml.model_loader import load_model


class Predictor:
    """Загружает обученную модель и проверяет входные данные перед прогнозом."""

    def __init__(self, model_path: str | Path) -> None:
        self.model = load_model(model_path)
        # Модель хранит число признаков, на которых её обучили.
        self.n_features = getattr(self.model, "n_features_in_", None)
        if self.n_features is None:
            raise ValueError("У модели отсутствует атрибут n_features_in_.")

    def predict(self, features: list[float]) -> dict[str, Any]:
        """Возвращает прогноз и вероятности классов, если модель их поддерживает."""
        if len(features) != self.n_features:
            raise ValueError(
                f"Ожидалось признаков: {self.n_features}; получено: {len(features)}."
            )

        # scikit-learn принимает таблицу, поэтому один объект — одна строка.
        sample = np.asarray(features, dtype=float).reshape(1, -1)
        result: dict[str, Any] = {"prediction": self.model.predict(sample)[0]}
        if hasattr(self.model, "predict_proba"):
            result["proba"] = self.model.predict_proba(sample)[0].tolist()
        return result
