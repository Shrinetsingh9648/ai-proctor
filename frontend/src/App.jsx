// // import React, { useRef } from 'react';
// // import Camera       from './components/Camera';
// // import DetectionHUD from './components/DetectionHUD';
// // import ExamPanel    from './components/ExamPanel';
// // import { useProctor } from './hooks/useProctor';
// //
// // export default function App() {
// //   const videoRef = useRef(null);
// //   const { result, connected, error } = useProctor(videoRef);
// //   const isSuspicious = result.suspicion_score > 0;
// //
// //   return (
// //     <div className="app">
// //       <div className="topbar">
// //         <div>
// //           <div className="topbar-title">Data Structures — Midterm Exam</div>
// //           <div className="topbar-sub">AI-monitored · Stay on camera</div>
// //         </div>
// //         <div className={connected ? 'badge-green' : 'badge-red'}>
// //           {connected ? 'Proctoring active' : 'Connecting...'}
// //         </div>
// //       </div>
// //
// //       {error && <div className="error-banner">{error}</div>}
// //
// //       <div className="grid">
// //         <ExamPanel />
// //         <div className="right-col">
// //           <Camera videoRef={videoRef} isSuspicious={isSuspicious} />
// //           <DetectionHUD result={result} connected={connected} />
// //         </div>
// //       </div>
// //     </div>
// //   );
// // }
//
//
//
//
//
//
// import React, { useRef, useState } from 'react';
// import Camera          from './components/Camera';
// import DetectionHUD    from './components/DetectionHUD';
// import ExamPanel       from './components/ExamPanel';
// import AdminDashboard  from './components/AdminDashboard';
// import { useProctor }  from './hooks/useProctor';
//
// export default function App() {
//   const videoRef = useRef(null);
//   const { result, connected, error } = useProctor(videoRef);
//   const isSuspicious = result.suspicion_score > 0;
//   const [view, setView] = useState('exam');  // 'exam' or 'admin'
//
//   return (
//     <div className="app">
//       {/* Top bar */}
//       <div className="topbar">
//         <div>
//           <div className="topbar-title">AI Proctor System</div>
//           <div className="topbar-sub">AI-monitored · Stay on camera</div>
//         </div>
//         <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
//           <button
//             onClick={() => setView('exam')}
//             style={{
//               padding: '6px 14px', borderRadius: '8px', border: 'none',
//               cursor: 'pointer', fontSize: '13px', fontWeight: '500',
//               background: view === 'exam' ? '#2563eb' : '#1e293b',
//               color: view === 'exam' ? '#fff' : '#94a3b8',
//             }}
//           >
//             Exam View
//           </button>
//           <button
//             onClick={() => setView('admin')}
//             style={{
//               padding: '6px 14px', borderRadius: '8px', border: 'none',
//               cursor: 'pointer', fontSize: '13px', fontWeight: '500',
//               background: view === 'admin' ? '#2563eb' : '#1e293b',
//               color: view === 'admin' ? '#fff' : '#94a3b8',
//             }}
//           >
//             Admin Dashboard
//           </button>
//           <div className={connected ? 'badge-green' : 'badge-red'}>
//             {connected ? 'Proctoring active' : 'Connecting...'}
//           </div>
//         </div>
//       </div>
//
//       {/* Error banner */}
//       {error && <div className="error-banner">{error}</div>}
//
//       {/* Views */}
//       {view === 'exam' ? (
//         <div className="grid">
//           <ExamPanel />
//           <div className="right-col">
//             <Camera videoRef={videoRef} isSuspicious={isSuspicious} />
//             <DetectionHUD result={result} connected={connected} />
//           </div>
//         </div>
//       ) : (
//         <AdminDashboard />
//       )}
//     </div>
//   );
// }




import React, { useRef, useState, useEffect } from 'react';
import Camera          from './components/Camera';
import DetectionHUD    from './components/DetectionHUD';
import ExamPanel       from './components/ExamPanel';
import AdminDashboard  from './components/AdminDashboard';
import LoginPage       from './components/LoginPage';
import { useProctor }  from './hooks/useProctor';

export default function App() {
  const videoRef = useRef(null);
  const [user, setUser]   = useState(null);
  const [view, setView]   = useState('exam');

  // Check if already logged in
  useEffect(() => {
    const token    = localStorage.getItem('token');
    const role     = localStorage.getItem('role');
    const username = localStorage.getItem('username');
    if (token) {
      setUser({ token, role, username });
      if (role === 'admin') setView('admin');
    }
  }, []);

  function handleLogin(data) {
    setUser(data);
    if (data.role === 'admin') setView('admin');
    else setView('exam');
  }

  function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    setUser(null);
  }

  // Show login page if not logged in
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

  return (
    <div className="app">
      {/* Tab switch warning banner */}
      {tabWarning && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999,
          background: '#dc2626', color: '#fff',
          padding: '14px', textAlign: 'center',
          fontSize: '15px', fontWeight: '600',
          animation: 'pulse 0.5s infinite',
        }}>
          ⚠️ WARNING: Tab switching detected! This has been logged. ({tabSwitchCount} time{tabSwitchCount !== 1 ? 's' : ''})
        </div>
      )}

      {/* Top bar */}
      <div className="topbar" style={{ marginTop: tabWarning ? '50px' : '0' }}>
        <div>
          <div className="topbar-title">AI Proctor System</div>
          <div className="topbar-sub">
            Logged in as <strong style={{ color: '#60a5fa' }}>{user.username}</strong>
            {' '}({user.role})
            {tabSwitchCount > 0 && (
              <span style={{ color: '#f87171', marginLeft: '12px' }}>
                ⚠️ Tab switches: {tabSwitchCount}
              </span>
            )}
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {user.role === 'student' && (
            <button onClick={() => setView('exam')} style={{
              padding: '6px 14px', borderRadius: '8px', border: 'none',
              cursor: 'pointer', fontSize: '13px', fontWeight: '500',
              background: view === 'exam' ? '#2563eb' : '#1e293b',
              color: view === 'exam' ? '#fff' : '#94a3b8',
            }}>Exam View</button>
          )}
          {user.role === 'admin' && (
            <button onClick={() => setView('admin')} style={{
              padding: '6px 14px', borderRadius: '8px', border: 'none',
              cursor: 'pointer', fontSize: '13px', fontWeight: '500',
              background: view === 'admin' ? '#2563eb' : '#1e293b',
              color: view === 'admin' ? '#fff' : '#94a3b8',
            }}>Admin Dashboard</button>
          )}
          <div className={connected ? 'badge-green' : 'badge-red'}>
            {connected ? 'Proctoring active' : 'Connecting...'}
          </div>
          <button onClick={onLogout} style={{
            padding: '6px 14px', borderRadius: '8px', border: 'none',
            cursor: 'pointer', fontSize: '13px',
            background: '#1e293b', color: '#f87171',
          }}>Logout</button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {view === 'exam' ? (
        <div className="grid">
          <ExamPanel />
          <div className="right-col">
            <Camera videoRef={videoRef} isSuspicious={isSuspicious} />
            <DetectionHUD result={result} connected={connected} />
          </div>
        </div>
      ) : (
        <AdminDashboard token={user.token} />
      )}
    </div>
  );
 }