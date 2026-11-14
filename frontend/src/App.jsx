import { useEffect, useState } from "react";
import axios from "axios";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./index.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [hotspots, setHotspots] = useState([]);
  const [location, setLocation] = useState("");
  const [night, setNight] = useState(false);
  const [drunkDriving, setDrunkDriving] = useState("No");
  const [overspeeding, setOverspeeding] = useState("No");

  const [prediction, setPrediction] = useState(null);
  const [alert, setAlert] = useState(null);

  const [loadingHotspots, setLoadingHotspots] = useState(true);
  const [loadingPrediction, setLoadingPrediction] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);
  const [error, setError] = useState("");

  async function loadHotspots() {
    try {
      const response = await axios.get(`${API_URL}/hotspots`);

      setHotspots(response.data);
      setApiConnected(true);
      setError("");
    } catch (err) {
      console.error(err);
      setApiConnected(false);
      setError(
        "Unable to connect to the SafeRoute backend. Make sure the backend is running on port 8000."
      );
    } finally {
      setLoadingHotspots(false);
    }
  }

  function fetchHotspots() {
    setLoadingHotspots(true);
    void loadHotspots();
  }

  // Get accident hotspots from backend
  useEffect(() => {
    void loadHotspots();
  }, []);

  // Predict risk
  const predictRisk = async (event) => {
    event.preventDefault();

    if (!location.trim()) {
      setError("Please select a location.");
      return;
    }

    try {
      setLoadingPrediction(true);
      setError("");
      setPrediction(null);
      setAlert(null);

      const response = await axios.post(`${API_URL}/predict-risk`, {
        location: location,
        night: night,
        drunk_driving: drunkDriving,
        overspeeding: overspeeding,
      });

      setPrediction(response.data);

      // Also check alert for the selected location
      try {
        const alertResponse = await axios.get(
          `${API_URL}/alerts?location=${encodeURIComponent(location)}`
        );

        setAlert(alertResponse.data);
      } catch (alertError) {
        console.error("Alert check failed:", alertError);
      }
    } catch (err) {
      console.error(err);

      if (err.response?.status === 404) {
        setError(
          "Location not found. Please select a location from the hotspot list."
        );
      } else {
        setError(
          "Unable to calculate risk. Please make sure the backend is running."
        );
      }
    } finally {
      setLoadingPrediction(false);
    }
  };

  // Risk color
  const getRiskColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case "high":
        return "#dc2626";
      case "moderate":
        return "#f59e0b";
      case "low":
        return "#16a34a";
      default:
        return "#64748b";
    }
  };

  // Risk background
  const getRiskClass = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case "high":
        return "risk-high";
      case "moderate":
        return "risk-moderate";
      case "low":
        return "risk-low";
      default:
        return "risk-default";
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div>
            <h1>🛣️ SafeRoute</h1>
            <p>Road Accident Risk Prediction & Traffic Safety</p>
          </div>

          <div className="status">
            <span className={`status-dot ${apiConnected ? "connected" : "disconnected"}`}></span>
            {apiConnected ? "API Connected" : "API Disconnected"}
          </div>
        </div>
      </header>

      <main className="container">
        {/* Error */}
        {error && (
          <div className="error-message">
            <strong>⚠️ Error:</strong> {error}
          </div>
        )}

        {/* Dashboard stats */}
        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📍</div>
            <div>
              <span className="stat-label">Locations</span>
              <strong>{hotspots.length}</strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🔴</div>
            <div>
              <span className="stat-label">High Risk</span>
              <strong>
                {
                  hotspots.filter(
                    (item) => item.risk_level?.toLowerCase() === "high"
                  ).length
                }
              </strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🟡</div>
            <div>
              <span className="stat-label">Moderate Risk</span>
              <strong>
                {
                  hotspots.filter(
                    (item) => item.risk_level?.toLowerCase() === "moderate"
                  ).length
                }
              </strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🟢</div>
            <div>
              <span className="stat-label">Low Risk</span>
              <strong>
                {
                  hotspots.filter(
                    (item) => item.risk_level?.toLowerCase() === "low"
                  ).length
                }
              </strong>
            </div>
          </div>
        </section>

        {/* Main content */}
        <section className="main-grid">
          {/* Map */}
          <div className="card map-card">
            <div className="card-header">
              <div>
                <h2>Accident Risk Map</h2>
                <p>Accident hotspots across the available locations</p>
              </div>

              <button className="refresh-button" onClick={fetchHotspots}>
                ↻ Refresh
              </button>
            </div>

            <div className="map-wrapper">
              {loadingHotspots ? (
                <div className="map-loading">
                  <div className="spinner"></div>
                  <p>Loading accident hotspots...</p>
                </div>
              ) : hotspots.length > 0 ? (
                <MapContainer
                  center={[17.98, 79.6]}
                  zoom={10}
                  scrollWheelZoom={true}
                  className="map"
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />

                  {hotspots.map((spot, index) => (
                    <CircleMarker
                      key={`${spot.location}-${index}`}
                      center={[spot.latitude, spot.longitude]}
                      radius={Math.max(
                        8,
                        Math.min(20, (spot.accident_count || 1) / 20)
                      )}
                      pathOptions={{
                        color: getRiskColor(spot.risk_level),
                        fillColor: getRiskColor(spot.risk_level),
                        fillOpacity: 0.65,
                        weight: 2,
                      }}
                    >
                      <Popup>
                        <div className="popup">
                          <h3>{spot.location}</h3>

                          <p>
                            <strong>Risk:</strong>{" "}
                            <span
                              style={{
                                color: getRiskColor(spot.risk_level),
                              }}
                            >
                              {spot.risk_level}
                            </span>
                          </p>

                          <p>
                            <strong>Accidents:</strong>{" "}
                            {spot.accident_count}
                          </p>

                          <p>
                            <strong>Fatal count:</strong>{" "}
                            {spot.fatal_count}
                          </p>

                          <p>
                            <strong>Prediction Confidence:</strong>{" "}
                            {spot.avg_risk_score}
                          </p>
                        </div>
                      </Popup>
                    </CircleMarker>
                  ))}
                </MapContainer>
              ) : (
                <div className="map-loading">
                  <p>No hotspot data available.</p>
                </div>
              )}
            </div>

            <div className="legend">
              <span>
                <i className="legend-dot low"></i> Low
              </span>

              <span>
                <i className="legend-dot moderate"></i> Moderate
              </span>

              <span>
                <i className="legend-dot high"></i> High
              </span>
            </div>
          </div>

          {/* Risk prediction */}
          <div className="card prediction-card">
            <div className="card-header">
              <div>
                <h2>Check Route Risk</h2>
                <p>Predict accident risk for a location</p>
              </div>
            </div>

            <form onSubmit={predictRisk}>
              <label>Location</label>

              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              >
                <option value="">Select a location</option>

                {hotspots.map((spot, index) => (
                  <option key={`${spot.location}-${index}`} value={spot.location}>
                    {spot.location}
                  </option>
                ))}
              </select>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={night}
                  onChange={(e) => setNight(e.target.checked)}
                />

                <span>🌙 Night-time driving</span>
              </label>

              <label>Drunk driving</label>

              <select
                value={drunkDriving}
                onChange={(e) => setDrunkDriving(e.target.value)}
              >
                <option value="No">No</option>
                <option value="Yes">Yes</option>
              </select>

              <label>Overspeeding</label>

              <select
                value={overspeeding}
                onChange={(e) => setOverspeeding(e.target.value)}
              >
                <option value="No">No</option>
                <option value="Yes">Yes</option>
              </select>

              <button
                type="submit"
                className="predict-button"
                disabled={loadingPrediction}
              >
                {loadingPrediction
                  ? "Calculating..."
                  : "🔍 Check Risk"}
              </button>
            </form>
          </div>
        </section>

        {/* Prediction result */}
        {prediction && (
          <section className="card result-card">
            <div className="result-header">
              <div>
                <span className="result-label">Risk Prediction</span>
                <h2>{prediction.location}</h2>
              </div>

              <div
                className={`risk-badge ${getRiskClass(
                  prediction.risk_level
                )}`}
              >
                {prediction.risk_level}
              </div>
            </div>

            <div className="result-grid">
              <div className="score-box">
                <span>Prediction Confidence</span>

                <strong>
                  {typeof prediction.risk_score === "number"
                    ? `${Math.round(prediction.risk_score * 100)}%`
                    : prediction.risk_score}
                </strong>
              </div>

              <div className="probability-box">
                <span>Class Probabilities</span>

                {prediction.class_probabilities &&
                  Object.entries(prediction.class_probabilities).map(
                    ([level, value]) => (
                      <div className="probability-row" key={level}>
                        <span>{level}</span>

                        <div className="progress">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${Math.min(
                                100,
                                Number(value) * 100
                              )}%`,
                              background: getRiskColor(level),
                            }}
                          ></div>
                        </div>

                        <strong>
                          {(Number(value) * 100).toFixed(1)}%
                        </strong>
                      </div>
                    )
                  )}
              </div>

              <div className="factors-box">
                <span>Contributing Factors</span>

                {prediction.contributing_factors?.length > 0 ? (
                  <ul>
                    {prediction.contributing_factors.map(
                      (factor, index) => (
                        <li key={index}>{factor}</li>
                      )
                    )}
                  </ul>
                ) : (
                  <p>No additional contributing factors.</p>
                )}
              </div>
            </div>
          </section>
        )}

        {/* Alert */}
        {alert && (
          <section
            className={`alert-banner ${
              alert.alert ? "alert-danger" : "alert-safe"
            }`}
          >
            <div className="alert-icon">
              {alert.alert ? "⚠️" : "✅"}
            </div>

            <div>
              <strong>
                {alert.alert
                  ? "High Risk Alert"
                  : "Location Safety Status"}
              </strong>

              <p>{alert.message}</p>
            </div>
          </section>
        )}

        {/* Locations table */}
        <section className="card locations-card">
          <div className="card-header">
            <div>
              <h2>Accident Hotspots</h2>
              <p>Historical accident information by location</p>
            </div>
          </div>

          {loadingHotspots ? (
            <p>Loading...</p>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Location</th>
                    <th>Accidents</th>
                    <th>Fatal Count</th>
                    <th>Average Risk</th>
                    <th>Risk Level</th>
                  </tr>
                </thead>

                <tbody>
                  {hotspots.map((spot, index) => (
                    <tr key={`${spot.location}-row-${index}`}>
                      <td>
                        <strong>{spot.location}</strong>
                      </td>

                      <td>{spot.accident_count}</td>

                      <td>{spot.fatal_count}</td>

                      <td>{spot.avg_risk_score}</td>

                      <td>
                        <span
                          className={`table-risk ${getRiskClass(
                            spot.risk_level
                          )}`}
                        >
                          {spot.risk_level}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      <footer>
        <p>
          SafeRoute • Road Accident Risk Prediction & Traffic Safety
        </p>
      </footer>
    </div>
  );
}

export default App;