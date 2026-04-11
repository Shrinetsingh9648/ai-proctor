import React, { useRef, useState, useEffect } from 'react';
import Camera            from './components/Camera';
import DetectionHUD      from './components/DetectionHUD';
import ExamPanel         from './components/ExamPanel';
import AdminDashboard    from './components/AdminDashboard';
import LoginPage         from './components/LoginPage';
import QuestionManager   from './components/QuestionManager';
import ExamResults       from './components/ExamResults';
import { useProctor }    from './hooks/useProctor';

export default function App() {
  const videoRef = useRef(null);
  const [user, setUser] = useState(null);
  const [view, setView] = useState('exam');

  useEffect(() => {
    const token    = localStorage.getItem('token');
    const role     = localStorage.getItem('role');
    const username = localStorage.getItem('username');
    if (token) {
      setUser({ token, role, username });
      if (role === 'admin') setView('dashboard');
    }
  }, []);

  function handleLogin(data) {
    setUser(data);
    setView(data.role === 'admin' ? 'dashboard' : 'exam');
  }

  function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    setUser(null);
  }

  if (!user) return <LoginPage onLogin={handleLogin} />;

  return (
    <AppInner
      user={user}
      view={view}
      setView={setView}
      videoRef={videoRef}
      onLogout={handleLogout}
    />
  );
}

function AppInner({ user, view, setView, videoRef, onLogout }) {
  const { result, connected, error, tabSwitchCount, tabWarning } = useProctor(videoRef, user.token);
  const isSuspicious = result.suspicion_score > 0;

  const adminViews = [
    { key: 'dashboard', label: '📊 Dashboard' },
    { key: 'questions', label: '📝 Questions' },
    { key: 'results',   label: '🏆 Results'   },
  ];

  return (
    <div className="app">

      {/* Tab switch warning banner */}
      {tabWarning && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999,
          background: 'linear-gradient(135deg, #dc2626, #991b1b)',
          color: '#fff', padding: '14px',
          textAlign: 'center', fontSize: '14px', fontWeight: '600',
          boxShadow: '0 4px 20px rgba(239,68,68,0.4)',
          animation: 'slideIn 0.3s ease',
        }}>
          ⚠️ WARNING: Tab switching detected! This has been logged.
          ({tabSwitchCount} time{tabSwitchCount !== 1 ? 's' : ''})
        </div>
      )}

      {/* Top bar */}
      <div className="topbar" style={{ marginTop: tabWarning ? '54px' : '0' }}>
        <div>
          <div className="topbar-title">🛡️ AI Proctor System</div>
          <div className="topbar-sub">
            Logged in as{' '}
            <strong style={{
              color: user.role === 'admin' ? '#a78bfa' : '#60a5fa'
            }}>
              {user.username}
            </strong>
            {' '}·{' '}
            <span style={{
              color: user.role === 'admin' ? '#a78bfa' : '#60a5fa'
            }}>
              {user.role}
            </span>
            {tabSwitchCount > 0 && (
              <span style={{ color: '#f87171', marginLeft: '12px' }}>
                ⚠️ {tabSwitchCount} tab switch{tabSwitchCount !== 1 ? 'es' : ''}
              </span>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>

          {/* Admin navigation */}
          {user.role === 'admin' && adminViews.map(v => (
            <button
              key={v.key}
              onClick={() => setView(v.key)}
              className={`nav-btn ${view === v.key ? 'active' : ''}`}
            >
              {v.label}
            </button>
          ))}

          {/* Student navigation */}
          {user.role === 'student' && (
            <button
              onClick={() => setView('exam')}
              className="nav-btn active"
            >
              📝 Exam
            </button>
          )}

          {/* Proctoring status badge */}
          <div className={connected ? 'badge-green' : 'badge-red'}>
            {connected ? '🟢 Proctoring active' : '🔴 Connecting...'}
          </div>

          {/* Logout button */}
          <button
            onClick={onLogout}
            style={{
              padding: '7px 16px',
              borderRadius: '8px',
              border: '1px solid rgba(239,68,68,0.3)',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500',
              background: 'rgba(239,68,68,0.1)',
              color: '#f87171',
              transition: 'all 0.2s ease',
              fontFamily: 'Inter, sans-serif',
            }}
          >
            Logout
          </button>

        </div>
      </div>

      {/* Error banner */}
      {error && <div className="error-banner">{error}</div>}

      {/* Views */}
      {view === 'exam' && (
        <div className="grid" style={{ animation: 'fadeIn 0.4s ease' }}>
          <ExamPanel token={user.token} />
          <div className="right-col">
            <Camera videoRef={videoRef} isSuspicious={isSuspicious} />
            <DetectionHUD result={result} connected={connected} />
          </div>
        </div>
      )}

      {view === 'dashboard' && (
        <AdminDashboard token={user.token} />
      )}

      {view === 'questions' && (
        <QuestionManager token={user.token} />
      )}

      {view === 'results' && (
        <ExamResults token={user.token} />
      )}

    </div>
  );
}