import React, { useState, useEffect } from 'react';

export default function AdminDashboard({ token }) {
  const [logs, setLogs]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

//   function fetchLogs() {
//     setLoading(true);
//     fetch('http://localhost:8000/logs')
//       .then(r => r.json())
//       .then(data => { setLogs(data); setLoading(false); })
//       .catch(() => { setError('Cannot reach backend'); setLoading(false); });
//    function fetchLogs() {
//     setLoading(true);
//     fetch('http://localhost:8000/logs', {
//       headers: { 'Authorization': `Bearer ${token}` }
//     })
//       .then(r => r.json())
//       .then(data => { setLogs(data); setLoading(false); })
//       .catch(() => { setError('Cannot reach backend'); setLoading(false); });
//      }

function fetchLogs() {
    setLoading(true);
    fetch(`https://${process.env.REACT_APP_BACKEND_URL || 'localhost:8000'}/logs` , {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => {
        // Make sure data is always an array
        setLogs(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => { setError('Cannot reach backend'); setLoading(false); });
  }


  // Auto-refresh every 5 seconds
  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  // Summary counts
  const total    = logs.length;
  const phones   = logs.filter(l => l.event === 'phone_detected').length;
  const noface   = logs.filter(l => l.event === 'no_face').length;
  const looking  = logs.filter(l => l.event === 'looking_away').length;
  const multiple = logs.filter(l => l.event === 'multiple_faces').length;

  function eventColor(event) {
    if (event === 'phone_detected')  return 'pill pill-red';
    if (event === 'multiple_faces')  return 'pill pill-red';
    if (event === 'no_face')         return 'pill pill-red';
    if (event === 'looking_away')    return 'pill pill-yellow';
    return 'pill pill-green';
  }

  function formatTime(ts) {
    if (!ts) return '';
    return new Date(ts).toLocaleTimeString();
  }

  return (
    <div className="app">
      {/* Header */}
      <div className="topbar">
        <div>
          <div className="topbar-title">Admin Dashboard</div>
          <div className="topbar-sub">Live session logs — auto-refreshes every 5s</div>
        </div>
        <button
          onClick={fetchLogs}
          style={{
            background: '#2563eb', color: '#fff', border: 'none',
            padding: '8px 16px', borderRadius: '8px', cursor: 'pointer',
            fontSize: '13px'
          }}
        >
          Refresh now
        </button>
      </div>

      {/* Summary cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        {[
          { label: 'Total Events',     value: total,    color: '#60a5fa' },
          { label: 'Phone Detected',   value: phones,   color: '#f87171' },
          { label: 'Looking Away',     value: looking,  color: '#fbbf24' },
          { label: 'No Face / Multi',  value: noface + multiple, color: '#f87171' },
        ].map((card, i) => (
          <div key={i} style={{
            background: '#1e293b', borderRadius: '12px',
            padding: '16px', textAlign: 'center'
          }}>
            <div style={{ fontSize: '32px', fontWeight: '700', color: card.color }}>
              {card.value}
            </div>
            <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
              {card.label}
            </div>
          </div>
        ))}
      </div>

      {/* Logs table */}
      <div style={{ background: '#1e293b', borderRadius: '12px', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #334155' }}>
          <span style={{ fontWeight: '600', color: '#fff' }}>
            Session Logs {loading && '(refreshing...)'}
          </span>
        </div>

        {error && <div className="error-banner" style={{ margin: '16px' }}>{error}</div>}

        {logs.length === 0 && !loading && (
          <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
            No events yet. Trigger a detection on the exam page first.
          </div>
        )}

        {logs.length > 0 && (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#0f172a' }}>
                {['ID', 'Student', 'Event', 'Score', 'Time'].map(h => (
                  <th key={h} style={{
                    padding: '10px 16px', textAlign: 'left',
                    fontSize: '11px', color: '#64748b',
                    textTransform: 'uppercase', letterSpacing: '0.05em'
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id} style={{ borderBottom: '1px solid #1e293b' }}>
                  <td style={{ padding: '10px 16px', color: '#475569', fontSize: '13px' }}>
                    #{log.id}
                  </td>
                  <td style={{ padding: '10px 16px', color: '#cbd5e1', fontSize: '13px' }}>
                    {log.user_id}
                  </td>
                  <td style={{ padding: '10px 16px' }}>
                    <span className={eventColor(log.event)}>{log.event}</span>
                  </td>
                  <td style={{ padding: '10px 16px', fontSize: '13px', fontWeight: '600',
                    color: log.suspicion_score >= 50 ? '#f87171' :
                           log.suspicion_score >= 20 ? '#fbbf24' : '#4ade80' }}>
                    {log.suspicion_score}
                  </td>
                  <td style={{ padding: '10px 16px', color: '#64748b', fontSize: '12px' }}>
                    {formatTime(log.timestamp)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}