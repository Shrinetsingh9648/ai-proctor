import React, { useState, useEffect } from 'react';

export default function ExamResults({ token }) {
  const [results, setResults] = useState([]);

  const BACKEND = process.env.REACT_APP_BACKEND_URL || 'localhost:8000';

  useEffect(() => {
    fetch(`http://localhost:8000/exam/results` , {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => setResults(Array.isArray(data) ? data : []));
  }, [token, BACKEND]);

  function formatDate(ts) {
    if (!ts) return '';
    return new Date(ts).toLocaleString();
  }

  const avg = results.length
    ? Math.round(results.reduce((a, r) => a + (r.score / r.total_questions * 100), 0) / results.length)
    : 0;

  const passed = results.filter(r => r.score / r.total_questions >= 0.6).length;

  return (
    <div className="app">
      <div className="topbar">
        <div>
          <div className="topbar-title">Exam Results</div>
          <div className="topbar-sub">{results.length} submissions</div>
        </div>
      </div>

      {/* Summary cards */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3,1fr)',
        gap: '16px', marginBottom: '24px'
      }}>
        {[
          { label: 'Total Submissions', value: results.length, color: '#60a5fa' },
          { label: 'Average Score', value: `${avg}%`, color: '#fbbf24' },
          { label: 'Passed', value: passed, color: '#4ade80' },
        ].map((c, i) => (
          <div key={i} style={{
            background: '#1e293b', borderRadius: '12px',
            padding: '16px', textAlign: 'center'
          }}>
            <div style={{ fontSize: '32px', fontWeight: '700', color: c.color }}>
              {c.value}
            </div>
            <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
              {c.label}
            </div>
          </div>
        ))}
      </div>

      {/* Results table */}
      <div style={{ background: '#1e293b', borderRadius: '12px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#0f172a' }}>
              {['Student', 'Score', 'Percentage', 'Status', 'Submitted'].map(h => (
                <th key={h} style={{
                  padding: '10px 16px', textAlign: 'left',
                  fontSize: '11px', color: '#64748b', textTransform: 'uppercase'
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map(r => {
              const pct = Math.round(r.score / r.total_questions * 100);
              const passed = pct >= 60;
              return (
                <tr key={r.id} style={{ borderBottom: '1px solid #0f172a' }}>
                  <td style={{ padding: '12px 16px', color: '#cbd5e1', fontSize: '13px' }}>
                    {r.student_id}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '13px', fontWeight: '600',
                    color: passed ? '#4ade80' : '#f87171' }}>
                    {r.score}/{r.total_questions}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{
                        height: '6px', width: '80px',
                        background: '#334155', borderRadius: '3px', overflow: 'hidden'
                      }}>
                        <div style={{
                          height: '100%', width: `${pct}%`,
                          background: passed ? '#4ade80' : '#f87171',
                          borderRadius: '3px'
                        }} />
                      </div>
                      <span style={{ color: passed ? '#4ade80' : '#f87171',
                        fontSize: '13px', fontWeight: '600' }}>
                        {pct}%
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      background: passed ? '#14532d' : '#7f1d1d',
                      color: passed ? '#86efac' : '#fca5a5',
                      padding: '2px 10px', borderRadius: '999px', fontSize: '11px'
                    }}>
                      {passed ? 'Passed' : 'Failed'}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', color: '#64748b', fontSize: '12px' }}>
                    {formatDate(r.submitted_at)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {results.length === 0 && (
          <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
            No results yet.
          </div>
        )}
      </div>
    </div>
  );
}