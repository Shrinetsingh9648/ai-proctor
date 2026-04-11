import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function AdminDashboard({ token }) {
  const [logs, setLogs]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  function fetchLogs() {
    setLoading(true);
    fetch('http://localhost:8000/logs', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => { setLogs(Array.isArray(data) ? data : []); setLoading(false); })
      .catch(() => { setError('Cannot reach backend'); setLoading(false); });
  }

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const total    = logs.length;
  const phones   = logs.filter(l => l.event === 'phone_detected').length;
  const noface   = logs.filter(l => l.event === 'no_face').length;
  const looking  = logs.filter(l => l.event === 'looking_away').length;
  const multiple = logs.filter(l => l.event === 'multiple_faces').length;
  const tabs     = logs.filter(l => l.event === 'tab_switch').length;

  // Chart data
  const barData = [
    { name: 'Phone', value: phones,   color: '#ef4444' },
    { name: 'No Face', value: noface, color: '#f59e0b' },
    { name: 'Looking Away', value: looking, color: '#3b82f6' },
    { name: 'Multi Face', value: multiple, color: '#8b5cf6' },
    { name: 'Tab Switch', value: tabs, color: '#ec4899' },
  ].filter(d => d.value > 0);

  function eventColor(event) {
    const map = {
      phone_detected: 'pill pill-red',
      multiple_faces: 'pill pill-red',
      no_face:        'pill pill-yellow',
      looking_away:   'pill pill-yellow',
      tab_switch:     'pill pill-yellow',
    };
    return map[event] || 'pill pill-green';
  }

  function formatTime(ts) {
    if (!ts) return '';
    return new Date(ts).toLocaleTimeString();
  }

  const stats = [
    { label: 'Total Events',   value: total,           color: '#3b82f6' },
    { label: 'Phone Detected', value: phones,           color: '#ef4444' },
    { label: 'Looking Away',   value: looking,          color: '#f59e0b' },
    { label: 'Tab Switches',   value: tabs,             color: '#ec4899' },
  ];

  return (
    <div style={{ animation: 'fadeIn 0.4s ease' }}>
      {/* Header */}
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: '24px'
      }}>
        <div>
          <h2 style={{
            fontSize: '20px', fontWeight: '700',
            background: 'linear-gradient(135deg, #fff, #94a3b8)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
          }}>Admin Dashboard</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '2px' }}>
            Live monitoring · Auto-refreshes every 5s
            {loading && ' · Refreshing...'}
          </p>
        </div>
        <button onClick={fetchLogs} style={{
          background: 'rgba(59,130,246,0.1)',
          color: '#60a5fa',
          border: '1px solid rgba(59,130,246,0.3)',
          padding: '8px 16px', borderRadius: '8px',
          cursor: 'pointer', fontSize: '13px', fontWeight: '500',
          transition: 'all 0.2s ease', fontFamily: 'Inter, sans-serif'
        }}>
          ↻ Refresh
        </button>
      </div>

      {/* Stat cards */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(4,1fr)',
        gap: '16px', marginBottom: '24px'
      }}>
        {stats.map((s, i) => (
          <div key={i} className="stat-card" style={{
            animationDelay: `${i * 0.1}s`
          }}>
            <div className="stat-value" style={{ color: s.color }}>
              {s.value}
            </div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Chart */}
      {barData.length > 0 && (
        <div className="glass" style={{ padding: '20px', marginBottom: '24px' }}>
          <h3 style={{
            fontSize: '14px', fontWeight: '600',
            color: 'var(--text-secondary)', marginBottom: '16px',
            textTransform: 'uppercase', letterSpacing: '0.06em'
          }}>Event Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData} barSize={32}>
              <XAxis
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 12 }}
                axisLine={false} tickLine={false}
              />
              <YAxis
                tick={{ fill: '#64748b', fontSize: 11 }}
                axisLine={false} tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  background: '#0d1526',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#f1f5f9'
                }}
              />
              <Bar dataKey="value" radius={[6,6,0,0]}>
                {barData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Logs table */}
      <div className="glass" style={{ overflow: 'hidden' }}>
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', gap: '8px'
        }}>
          <div style={{
            width: '8px', height: '8px', borderRadius: '50%',
            background: '#4ade80',
            boxShadow: '0 0 8px #4ade80',
            animation: 'pulse 2s infinite'
          }} />
          <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>
            Session Logs
          </span>
          <span style={{
            background: 'rgba(59,130,246,0.15)',
            color: '#60a5fa', padding: '2px 8px',
            borderRadius: '999px', fontSize: '11px',
            fontWeight: '600'
          }}>{total}</span>
        </div>

        {error && <div className="error-banner" style={{ margin: '16px' }}>{error}</div>}

        {logs.length === 0 && !loading && (
          <div style={{
            padding: '48px', textAlign: 'center',
            color: 'var(--text-muted)'
          }}>
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>📊</div>
            <div>No events yet. Trigger detections on the exam page.</div>
          </div>
        )}

        {logs.length > 0 && (
          <table className="data-table">
            <thead>
              <tr>
                {['ID','Student','Event','Score','Time'].map(h => (
                  <th key={h}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td style={{ color: 'var(--text-muted)' }}>#{log.id}</td>
                  <td style={{ color: 'var(--text-primary)', fontWeight: '500' }}>
                    {log.user_id}
                  </td>
                  <td>
                    <span className={eventColor(log.event)}>{log.event}</span>
                  </td>
                  <td style={{
                    fontWeight: '700',
                    color: log.suspicion_score >= 50 ? '#f87171' :
                           log.suspicion_score >= 20 ? '#fbbf24' : '#4ade80'
                  }}>
                    {log.suspicion_score}
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
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