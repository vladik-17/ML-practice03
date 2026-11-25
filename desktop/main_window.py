"""Главное окно приложения."""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import DEFAULT_MODEL_NAME, FEATURE_NAMES, MODEL_PATHS
from desktop.worker import PredictWorker
from services.prediction_service import PredictionService


# Значения из первой строки датасета, в порядке FEATURE_NAMES.
EXAMPLE_FEATURE_VALUES = ("540", "0", "0", "162", "2,5", "1040", "676", "28")


class MainWindow(QMainWindow):
    """Окно для прогноза прочности бетона на сжатие."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Прогноз прочности бетона")
        self.resize(520, 420)
        self._worker: PredictWorker | None = None
        self._service = PredictionService(MODEL_PATHS[DEFAULT_MODEL_NAME])
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.model_combo = QComboBox()
        self.model_combo.addItems(MODEL_PATHS.keys())
        self.model_combo.setCurrentText(DEFAULT_MODEL_NAME)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.setVerticalSpacing(8)
        form.addRow("Модель:", self.model_combo)

        self.feature_edits: list[QLineEdit] = []
        for name, example in zip(FEATURE_NAMES, EXAMPLE_FEATURE_VALUES, strict=True):
            field = QLineEdit(example)
            field.returnPressed.connect(self.on_predict_clicked)
            form.addRow(name, field)
            self.feature_edits.append(field)
        layout.addLayout(form)

        self.predict_button = QPushButton("Предсказать")
        self.predict_button.clicked.connect(self.on_predict_clicked)
        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        actions = QHBoxLayout()
        actions.addWidget(self.predict_button, 1)
        actions.addWidget(self.clear_button)
        layout.addLayout(actions)

        self.result_label = QLabel("Результат появится здесь")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)
        layout.addStretch()
        self.setCentralWidget(central)

    @Slot(str)
    def on_model_changed(self, model_name: str) -> None:
        try:
            self._service.set_model(MODEL_PATHS[model_name])
            self.result_label.setText(f"Выбрана модель: {model_name}")
        except Exception as error:
            self.result_label.setText(f"Ошибка загрузки модели: {error}")

    @Slot()
    def on_predict_clicked(self) -> None:
        # Следующий расчёт можно запустить после завершения потока.
        if self._worker is not None:
            return

        values = []
        for name, field in zip(FEATURE_NAMES, self.feature_edits, strict=True):
            value = field.text().strip()
            if not value:
                self.result_label.setText(f"Заполните поле «{name}».")
                field.setFocus()
                return
            # Нормализуем десятичную запятую перед сборкой строки для сервиса.
            values.append(value.replace(",", "."))

        self.predict_button.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.result_label.setText("Вычисление...")
        # Окно получает результат или ошибку через сигналы потока.
        self._worker = PredictWorker(", ".join(values), self._service)
        self._worker.finished_ok.connect(self.on_success)
        self._worker.failed.connect(self.on_error)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    @Slot(str)
    def on_success(self, message: str) -> None:
        self.result_label.setText(message)
        self.predict_button.setEnabled(True)
        self.model_combo.setEnabled(True)

    @Slot(str)
    def on_error(self, message: str) -> None:
        self.result_label.setText(f"Ошибка: {message}")
        self.predict_button.setEnabled(True)
        self.model_combo.setEnabled(True)

    @Slot()
    def _on_worker_finished(self) -> None:
        self._worker = None

    @Slot()
    def on_clear_clicked(self) -> None:
        for field in self.feature_edits:
            field.clear()
        self.result_label.setText("Результат появится здесь")
