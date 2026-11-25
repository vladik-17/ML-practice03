"""Разбор ввода и получение прогноза от модели."""

from pathlib import Path

from ml.predictor import Predictor


class PredictionService:
    """Преобразует ввод в числа и передаёт их выбранной модели."""

    def __init__(self, model_path: str | Path) -> None:
        self.set_model(model_path)

    def set_model(self, model_path: str | Path) -> None:
        """Переключает сервис на другую сохранённую модель."""
        self.predictor = Predictor(model_path)

    @staticmethod
    def parse_features(raw_features: str) -> list[float]:
        if not raw_features.strip():
            raise ValueError("Введите значения признаков через запятую.")
        try:
            parts = [part.strip() for part in raw_features.split(",")]
            if any(not part for part in parts):
                raise ValueError
            return [float(part.replace(",", ".")) for part in parts]
        except ValueError as error:
            raise ValueError(
                "Все признаки должны быть числами."
            ) from error

    def run(self, raw_features: str) -> str:
        # Преобразуем ввод в числа и оформляем прогноз как текст для окна.
        features = self.parse_features(raw_features)
        result = self.predictor.predict(features)
        prediction = float(result["prediction"])
        return f"Прогноз прочности бетона: {prediction:.2f} МПа"
