import { useEffect, useMemo, useState } from "react";

const GATEWAY_BASE_URL = "http://localhost:8000";
const POLLING_INTERVAL_MS = 5000;

function App() {
  const [events, setEvents] = useState([]);
  const [sensorId, setSensorId] = useState("");
  const [eventType, setEventType] = useState("");
  const [sensorRegion, setSensorRegion] = useState("");

  const [limit, setLimit] = useState(25);
  const [page, setPage] = useState(1);
  const [sortOrder, setSortOrder] = useState("desc");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastUpdate, setLastUpdate] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  const offset = useMemo(() => {
    return (page - 1) * limit;
  }, [page, limit]);

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

    params.append("limit", String(limit));
    params.append("offset", String(offset));

    return params.toString();
  }, [sensorId, eventType, sensorRegion, limit, offset]);

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

      const sortedData = [...data].sort((a, b) => {
        const dateA = new Date(a.detected_at).getTime();
        const dateB = new Date(b.detected_at).getTime();
        return sortOrder === "desc" ? dateB - dateA : dateA - dateB;
      });

      setEvents(sortedData);
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
  }, [queryString, sortOrder]);

  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchEvents();
      fetchSystemStatus();
    }, POLLING_INTERVAL_MS);

    return () => clearInterval(intervalId);
  }, [queryString, sortOrder]);

  const clearFilters = () => {
    setSensorId("");
    setEventType("");
    setSensorRegion("");
    setLimit(25);
    setPage(1);
    setSortOrder("desc");
  };

  const goToNextPage = () => {
    if (events.length === limit) {
      setPage((prev) => prev + 1);
    }
  };

  const goToPreviousPage = () => {
    setPage((prev) => Math.max(1, prev - 1));
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
          <strong>Events shown in page:</strong> {events.length}
        </div>
        <div>
          <strong>Current page:</strong> {page}
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
            onChange={(e) => {
              setSensorId(e.target.value);
              setPage(1);
            }}
            placeholder="e.g. sensor-12"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="eventType">Event Type</label>
          <select
            id="eventType"
            value={eventType}
            onChange={(e) => {
              setEventType(e.target.value);
              setPage(1);
            }}
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
            onChange={(e) => {
              setSensorRegion(e.target.value);
              setPage(1);
            }}
            placeholder="e.g. north-zone"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="limit">Rows per page</label>
          <select
            id="limit"
            value={limit}
            onChange={(e) => {
              setLimit(Number(e.target.value));
              setPage(1);
            }}
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="sortOrder">Order</label>
          <select
            id="sortOrder"
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
          >
            <option value="desc">Newest first</option>
            <option value="asc">Oldest first</option>
          </select>
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
                  <td>{Number(event.dominant_frequency_hz).toFixed(2)}</td>
                  <td>{Number(event.peak_amplitude).toFixed(4)}</td>
                  <td>{event.replica_id}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      <section
        className="pagination-section"
      >
        <button onClick={goToPreviousPage} disabled={page === 1}>
          Previous
        </button>

        <span>
          Page <strong>{page}</strong>
        </span>

        <button onClick={goToNextPage} disabled={events.length < limit}>
          Next
        </button>
      </section>
    </div>
  );
}

export default App;