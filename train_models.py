"""Обучение и сохранение двух моделей регрессии для приложения."""

import csv
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from config import MODEL_PATHS


SEED = 12
DATA_PATH = Path(__file__).resolve().parent / "Concrete_Data.csv"


def main() -> None:
    with DATA_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file))
    if len(rows) < 2:
        raise ValueError("Датасет не содержит строк данных.")
    numeric_rows = [[float(value) for value in row] for row in rows[1:]]
    # Повторяем выборку из прошлой практики с тем же значением SEED.
    indices = np.random.default_rng(SEED).choice(
        len(numeric_rows), size=min(400, len(numeric_rows)), replace=False
    )
    sampled = [numeric_rows[index] for index in indices]
    # Последний столбец содержит измеренную прочность в МПа.
    features = [row[:-1] for row in sampled]
    target = [row[-1] for row in sampled]
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.3, random_state=SEED
    )

    # Pipeline сохраняет стандартизацию вместе с линейной моделью.
    models = {
        "Линейная регрессия": Pipeline(
            [("scaler", StandardScaler()), ("model", LinearRegression())]
        ),
        "Случайный лес": RandomForestRegressor(
            n_estimators=250, random_state=SEED, n_jobs=-1
        ),
    }
    for name, model in models.items():
        model.fit(x_train, y_train)
        prediction = model.predict(x_test)
        MODEL_PATHS[name].parent.mkdir(exist_ok=True)
        joblib.dump(model, MODEL_PATHS[name])
        rmse = mean_squared_error(y_test, prediction) ** 0.5
        print(f"{name}: RMSE={rmse:.3f} MPa; R2={r2_score(y_test, prediction):.3f}")


if __name__ == "__main__":
    main()
