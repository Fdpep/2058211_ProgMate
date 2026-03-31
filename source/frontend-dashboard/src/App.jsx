import { useEffect, useMemo, useState } from "react";

const GATEWAY_BASE_URL = "http://localhost:8000";
const POLLING_INTERVAL_MS = 5000;

function App() {
  const [events, setEvents] = useState([]);
  const [sensorId, setSensorId] = useState("");
  const [eventType, setEventType] = useState("");
  const [sensorRegion, setSensorRegion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastUpdate, setLastUpdate] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  const queryString = useMemo(() => {
    const params = new URLSearchParams();

    if (sensorId.trim()) {
      params.append("sensor_id", sensorId.trim());
    }

    if (eventType.trim()) {
      params.append("event_type", eventType.trim());
    }

    if (sensorRegion.trim()) {
      params.append("sensor_region", sensorRegion.trim());
    }

    params.append("limit", "100");
    params.append("offset", "0");

    return params.toString();
  }, [sensorId, eventType, sensorRegion]);

  const fetchEvents = async () => {
    setLoading(true);
    setError("");

    try {
      const url = `${GATEWAY_BASE_URL}/events?${queryString}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Gateway error: ${response.status}`);
      }

      const data = await response.json();
      setEvents(data);
      setLastUpdate(new Date());
    } catch (err) {
      setError(err.message || "Failed to fetch events.");
    } finally {
      setLoading(false);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${GATEWAY_BASE_URL}/system/status`);

      if (!response.ok) {
        throw new Error(`System status error: ${response.status}`);
      }

      const data = await response.json();
      setSystemStatus(data);
    } catch (err) {
      console.error(err.message || "Failed to fetch system status.");
    }
  };

  useEffect(() => {
    fetchEvents();
    fetchSystemStatus();
  }, [queryString]);

  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchEvents();
      fetchSystemStatus();
    }, POLLING_INTERVAL_MS);

    return () => clearInterval(intervalId);
  }, [queryString]);

  const clearFilters = () => {
    setSensorId("");
    setEventType("");
    setSensorRegion("");
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Distributed Seismic Dashboard</h1>
        <p>
          Real-time monitoring of detected seismic events retrieved through the gateway service.
        </p>
      </header>

      <section className="status-section">
        <div>
          <strong>Dashboard status:</strong> {loading ? "Loading..." : "Idle"}
        </div>
        <div>
          <strong>Events shown:</strong> {events.length}
        </div>
        <div>
          <strong>Last update:</strong>{" "}
          {lastUpdate ? lastUpdate.toLocaleString() : "Not available"}
        </div>
      </section>

      <section className="system-status-section">
        <h2>System Status</h2>

        {!systemStatus ? (
          <p>Loading system status...</p>
        ) : (
          <>
            <div>
              <strong>System:</strong> {systemStatus.status}
            </div>
            <div>
              <strong>Active replicas:</strong>{" "}
              {systemStatus.active_replicas} / {systemStatus.total_replicas}
            </div>

            <ul>
              {Object.entries(systemStatus.replicas).map(([replicaName, replicaState]) => (
                <li key={replicaName}>
                  {replicaName} →{" "}
                  <strong
                    style={{
                      color: replicaState === "UP" ? "green" : "red",
                    }}
                  >
                    {replicaState}
                  </strong>
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      <section className="filters-section">
        <div className="filter-group">
          <label htmlFor="sensorId">Sensor ID</label>
          <input
            id="sensorId"
            type="text"
            value={sensorId}
            onChange={(e) => setSensorId(e.target.value)}
            placeholder="e.g. sensor-12"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="eventType">Event Type</label>
          <select
            id="eventType"
            value={eventType}
            onChange={(e) => setEventType(e.target.value)}
          >
            <option value="">All</option>
            <option value="earthquake">earthquake</option>
            <option value="conventional_explosion">conventional_explosion</option>
            <option value="nuclear_like">nuclear_like</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="sensorRegion">Sensor Region</label>
          <input
            id="sensorRegion"
            type="text"
            value={sensorRegion}
            onChange={(e) => setSensorRegion(e.target.value)}
            placeholder="e.g. Replica Datacenter"
          />
        </div>

        <div className="actions-group">
          <button onClick={fetchEvents}>Refresh</button>
          <button onClick={clearFilters} className="secondary-button">
            Clear filters
          </button>
        </div>
      </section>

      {error && (
        <section className="error-box">
          <strong>Error:</strong> {error}
        </section>
      )}

      <section className="table-section">
        <table>
          <thead>
            <tr>
              <th>Detected At</th>
              <th>Sensor ID</th>
              <th>Sensor Name</th>
              <th>Region</th>
              <th>Event Type</th>
              <th>Frequency (Hz)</th>
              <th>Peak Amplitude</th>
              <th>Replica</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr>
                <td colSpan="8" className="empty-row">
                  No events found for the selected filters.
                </td>
              </tr>
            ) : (
              events.map((event) => (
                <tr key={event.event_id}>
                  <td>{new Date(event.detected_at).toLocaleString()}</td>
                  <td>{event.sensor_id}</td>
                  <td>{event.sensor_name}</td>
                  <td>{event.sensor_region}</td>
                  <td>{event.event_type}</td>
                  <td>{event.dominant_frequency_hz.toFixed(2)}</td>
                  <td>{event.peak_amplitude.toFixed(4)}</td>
                  <td>{event.replica_id}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default App;