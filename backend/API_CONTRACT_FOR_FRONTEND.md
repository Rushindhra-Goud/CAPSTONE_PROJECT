# SafeRoute Backend API — Contract for Frontend

**Base URL (while I'm running it locally):** `http://127.0.0.1:8000`
**Interactive docs (you can test everything yourself here):** `http://127.0.0.1:8000/docs`

> Note: this only works while my server is running on my laptop. Once we deploy
> to Render/Railway, I'll update this doc with the real public URL.

---

## 1. GET /hotspots

Returns every location with accident stats — use this to plot markers/heatmap on the map.

**No parameters needed.**

**Sample response:**
```json
[
  {
    "location": "Kazipet Chowrastha",
    "accident_count": 294,
    "fatal_count": 602,
    "avg_risk_score": 0.356,
    "risk_level": "Moderate",
    "latitude": 17.9686,
    "longitude": 79.5101
  },
  {
    "location": "Parkal",
    "accident_count": 298,
    "fatal_count": 580,
    "avg_risk_score": 0.119,
    "risk_level": "Low",
    "latitude": 18.2001,
    "longitude": 79.8297
  }
]
```

Use `latitude`/`longitude` to place markers, `risk_level` (Low/Moderate/High) to color-code them, `accident_count` for marker size or a popup detail.

---

## 2. POST /predict-risk

Use this for your "check risk for a location" feature — e.g. a search box where the user picks a location.

**Request body:**
```json
{
  "location": "Kazipet",
  "night": true,
  "drunk_driving": "Yes",
  "overspeeding": "No"
}
```
- `location` (required, string) — must match a location name from `/hotspots`
- `night`, `drunk_driving`, `overspeeding` — optional, send only if your UI collects them
- `weather_condition` — optional; if you don't send it, the backend fetches live weather automatically

**Sample response:**
```json
{
  "location": "Kazipet",
  "risk_level": "Low",
  "risk_score": 0.87,
  "class_probabilities": {
    "High": 0.01,
    "Low": 0.87,
    "Moderate": 0.119
  },
  "contributing_factors": [
    "Drunk driving reported",
    "Night-time driving",
    "Weather condition: Cloudy"
  ]
}
```

Display `risk_level` prominently (color it: Low=green, Moderate=yellow, High=red), show `risk_score` as a confidence %, and list `contributing_factors` as bullet points.

---

## 3. GET /alerts?location=Kazipet

Simple alert check for a location — pass it as a query parameter in the URL, not a body.

**Example call:** `GET /alerts?location=Kazipet`

**Sample response:**
```json
{
  "location": "Kazipet",
  "alert": false,
  "message": "Kazipet currently shows a lower accident risk profile."
}
```

Use `alert` (true/false) to decide whether to show a warning banner, and `message` as the text to display.

---

## Important notes

- All valid `location` names come from `/hotspots` — call that first to get the list, don't hardcode location names.
- CORS is already enabled on my end, so you can call these directly from your React/JS app without extra setup.
- If you get a 404 on `/predict-risk`, it means the location name doesn't match anything in the database — double check spelling/casing against `/hotspots`.
