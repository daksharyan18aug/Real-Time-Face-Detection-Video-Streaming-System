import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
const POLL_INTERVAL_MS = 2000;

function ROITable({ sessionId, isStreaming }) {
  const [records, setRecords] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchROI = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/roi`, {
        params: { session_id: sessionId, limit: 20 },
      });
      setRecords(res.data);
      setError(null);
    } catch (err) {
      if (err.response?.status !== 404) {
        setError("Could not fetch ROI data");
      }
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Poll while streaming
  useEffect(() => {
    if (!sessionId) return;
    fetchROI();
    if (!isStreaming) return;
    const interval = setInterval(fetchROI, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [sessionId, isStreaming, fetchROI]);

  if (!sessionId) {
    return (
      <div className="roi-table-container">
        <h2>📊 ROI Detection Data</h2>
        <p className="no-data">Start streaming to see detection data</p>
      </div>
    );
  }

  return (
    <div className="roi-table-container">
      <h2>📊 ROI Detection Data</h2>

      {loading && records.length === 0 && <p>Loading...</p>}
      {error && <p className="error-box">{error}</p>}

      {records.length === 0 && !loading ? (
        <p className="no-data">No faces detected yet</p>
      ) : (
        <div className="table-wrapper">
          <table className="roi-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Frame ID</th>
                <th>X</th>
                <th>Y</th>
                <th>Width</th>
                <th>Height</th>
                <th>Confidence</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r, i) => (
                <tr key={r.id}>
                  <td>{i + 1}</td>
                  <td className="frame-id">{r.frame_id.split("_").pop()}</td>
                  <td>{r.x}</td>
                  <td>{r.y}</td>
                  <td>{r.width}</td>
                  <td>{r.height}</td>
                  <td>
                    <span className={`confidence ${r.confidence > 0.8 ? "high" : "low"}`}>
                      {(r.confidence * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td>{new Date(r.timestamp).toLocaleTimeString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ROITable;