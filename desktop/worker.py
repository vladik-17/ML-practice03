"""Фоновый поток расчёта прогноза."""

from PySide6.QtCore import QThread, Signal

from services.prediction_service import PredictionService


class PredictWorker(QThread):
    """Вызывает сервис в фоновом потоке, сохраняя отзывчивость окна."""

    finished_ok = Signal(str)
    failed = Signal(str)

    def __init__(self, raw_features: str, service: PredictionService) -> None:
        super().__init__()
        self._raw_features = raw_features
        self._service = service

    def run(self) -> None:
        # QThread вызывает run() в фоне после вызова start().
        try:
            self.finished_ok.emit(self._service.run(self._raw_features))
        except Exception as error:
            self.failed.emit(str(error))
