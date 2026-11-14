# SafeRoute Backend API

FastAPI backend for the SafeRoute road accident risk prediction platform (Warangal).
Runs the tuned XGBoost model (retrained with current library versions for
compatibility with modern Python/scikit-learn installs) on the exact
`cleaned_accidents.csv` (5000 records, 53 columns) it was trained on.

## Setup (VS Code)

1. Open this folder in VS Code.
2. `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`, add your free OpenWeatherMap key (optional).
6. `python load_data.py` — loads cleaned_accidents.csv into a local SQLite DB.
7. `python -m uvicorn main:app --reload`
8. Open http://127.0.0.1:8000/docs to test everything interactively.

## Important: if you see a pickle/version error

If `saferoute_risk_model.pkl` fails to load with an error mentioning
scikit-learn versions, it means your installed scikit-learn is older than
what this model was saved with. Fix: `pip install --upgrade scikit-learn xgboost`
(requirements.txt already specifies `>=` versions, not exact pins, so a normal
`pip install -r requirements.txt` should avoid this entirely on a fresh setup).

## Endpoints

- `POST /predict-risk` — body: `{"location": "Kazipet", "night": true, "drunk_driving": "Yes"}`
  Uses the trained XGBoost model. Builds the full 46-feature row from a
  representative historical record for the location, then overrides with
  any live inputs sent (weather, night, overspeeding, drunk_driving).
  Returns risk_level, risk_score (model confidence), class_probabilities,
  and contributing_factors.

- `GET /hotspots` — groups all 5000 records by location: accident_count,
  fatal_count, avg_risk_score, risk_level, lat/lon. Feeds the frontend map.

- `GET /alerts?location=Kazipet` — alert flag based on historical
  risk/blackspot proximity at that location.

## Model performance (for your report)

Tuned XGBoost: ~84.6% accuracy, ~0.84 weighted F1 on held-out test data.
Best hyperparameters: n_estimators=300, max_depth=3, learning_rate=0.05.

Interesting finding: `is_night` has weak correlation with risk_level in
the training data. `blackspot_distance_km` is the strongest predictor
(~5.0 km avg for Low-risk rows vs ~0.58 km for High-risk rows) --
location/proximity to a known blackspot matters far more than time of day.

## Files

- `services/saferoute_risk_model.pkl` -- tuned XGBoost pipeline
- `services/risk_label_encoder.pkl` -- decodes model output to Low/Moderate/High
- `services/ml_service.py` -- loads the model, builds features, predicts
- `cleaned_accidents.csv` -- the exact training data (also used as the DB source)
- `retrain_compatible_model.py` -- reproduces the model if you ever need to
  regenerate it on a different machine/library version

## Switching to Postgres later (Supabase/Railway)

Set `DATABASE_URL` in `.env` to your Postgres connection string, re-run
`python load_data.py`. No code changes needed elsewhere.
