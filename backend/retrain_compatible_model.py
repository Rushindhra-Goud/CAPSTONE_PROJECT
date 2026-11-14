"""
Re-runs Member 2's exact training logic (from SafeRoute__ML.ipynb) using
CURRENT library versions, so the resulting .pkl files are compatible with
whatever scikit-learn/xgboost pip installs on Python 3.14 (or any modern setup) --
avoiding the old-vs-new pickle incompatibility entirely.

Same steps, same hyperparameter grid, same random_state -- only the
library versions differ from the original Colab run.
"""
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier

df = pd.read_csv("cleaned_accidents.csv")

drop_columns = ["accident_id", "risk_score", "risk_level", "persons_injured", "persons_died", "severity"]
X = df.drop(columns=drop_columns)
y = df["risk_level"].replace({"Critical": "High"})  # same collapse as the original notebook

numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
categorical_features = X.select_dtypes(include=["object"]).columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

numeric_transformer = Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))])
categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])
preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features),
])

label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded = label_encoder.transform(y_test)

xgb_model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1,
        random_state=42, eval_metric="mlogloss", n_jobs=-1,
    )),
])

param_grid = {
    "classifier__n_estimators": [100, 200, 300, 500],
    "classifier__max_depth": [3, 4, 5, 6, 8],
    "classifier__learning_rate": [0.01, 0.05, 0.1, 0.2],
}

print("Tuning started (this reproduces Member 2's exact process)...")
xgb_tuning = RandomizedSearchCV(
    xgb_model, param_distributions=param_grid, n_iter=10,
    scoring="f1_weighted", cv=3, random_state=42, n_jobs=-1,
)
xgb_tuning.fit(X_train, y_train_encoded)
best_model = xgb_tuning.best_estimator_
print("Best parameters:", xgb_tuning.best_params_)

from sklearn.metrics import accuracy_score, f1_score
final_pred = best_model.predict(X_test)
print("Final Accuracy:", accuracy_score(y_test_encoded, final_pred))
print("Final F1 (weighted):", f1_score(y_test_encoded, final_pred, average="weighted", zero_division=0))

joblib.dump(best_model, "saferoute_risk_model.pkl")
joblib.dump(label_encoder, "risk_label_encoder.pkl")
print("Saved: saferoute_risk_model.pkl, risk_label_encoder.pkl (current library versions)")
