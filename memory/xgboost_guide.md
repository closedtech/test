# XGBoost — короткая методичка

## Что это

XGBoost (eXtreme Gradient Boosting) — библиотека градиентного бустинга на деревьях решений. Одна из самых мощных и популярных моделей для табличных данных.

## Установка

```bash
pip install xgboost
```

## Быстрый старт

```python
import xgboost as xgb
from sklearn.model_selection import train_test_split

# Данные
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Модель
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    objective='binary:logistic',  # или 'multi:softmax'
    eval_metric='logloss',
    use_label_encoder=False
)

model.fit(X_train, y_train)
preds = model.predict(X_test)
```

## Основные гиперпараметры

| Параметр | Что делает | Типичные значения |
|---|---|---|
| `n_estimators` | Число деревьев | 100–1000 |
| `max_depth` | Макс. глубина дерева | 3–10 |
| `learning_rate` (eta) | Скорость обучения | 0.01–0.3 |
| `subsample` | Доля данных для дерева | 0.5–1.0 |
| `colsample_bytree` | Доля фичей для дерева | 0.5–1.0 |
| `min_child_weight` | Мин. вес листа | 1–10 |
| `gamma` | Минимальное снижение loss | 0–5 |
| `reg_alpha` | L1-регуляризация | 0–1 |
| `reg_lambda` | L2-регуляризация | 1–∞ |

## Регрессия vs Классификация

```python
# Регрессия
model = xgb.XGBRegressor(objective='reg:squarederror')
# Классификация (бинарная)
model = xgb.XGBClassifier(objective='binary:logistic')
# Классификация (мультикласс)
model = xgb.XGBClassifier(objective='multi:softmax', num_class=3)
```

## Работа с дисбалансом классов

```python
model = xgb.XGBClassifier(
    scale_pos_weight=ratio  # отношение negative/positive
)
```

## Важность фичей

```python
# Важность по числу использований
xgb.plot_importance(model)

# Получить численно
importances = model.feature_importances_
```

## Ранняя остановка

```python
model = xgb.XGBClassifier(
    n_estimators=1000,
    early_stopping_rounds=50,
    eval_metric='logloss'
)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
```

## Советы

- **Масштабирование** — не обязательно, но желательно для стабильности
- **Пропуски** — XGBoost сам работает с NaN
- **Категориальные фичи** — закодируй заранее (label encoding / one-hot)
- **Переобучение** — увеличивай `min_child_weight`, уменьшай `max_depth`, ставь раннюю остановку
- **Подбор параметров** — `GridSearchCV` или `Optuna`

## DMatrix (внутренний формат XGBoost)

```python
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

params = {
    'max_depth': 6,
    'eta': 0.1,
    'objective': 'binary:logistic',
    'eval_metric': 'logloss'
}

bst = xgb.train(params, dtrain, num_boost_round=100)
preds = bst.predict(dtest)
```

## CLI и сохранение модели

```python
# Сохранить
model.save_model('model.json')

# Загрузить
model.load_model('model.json')
```

---

_Краткая шпаргалка. Для деталей — официальная docs: https://xgboost.readthedocs.io_
