import React, { useState } from 'react';

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  async function handleLogin() {
    if (!username || !password) {
      setError('Please enter username and password');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      const res  = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || 'Login failed'); setLoading(false); return; }
      localStorage.setItem('token',    data.access_token);
      localStorage.setItem('role',     data.role);
      localStorage.setItem('username', data.username);
      onLogin(data);
    } catch {
      setError('Cannot reach backend. Is the server running?');
    }
    setLoading(false);
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-primary)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background glow effects */}
      <div style={{
        position: 'absolute', width: '600px', height: '600px',
        background: 'radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%)',
        top: '-100px', left: '-100px', pointerEvents: 'none'
      }} />
      <div style={{
        position: 'absolute', width: '400px', height: '400px',
        background: 'radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 70%)',
        bottom: '-50px', right: '-50px', pointerEvents: 'none'
      }} />

      {/* Login card */}
      <div style={{
        background: 'rgba(255,255,255,0.04)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: '24px',
        padding: '48px 40px',
        width: '100%',
        maxWidth: '420px',
        animation: 'fadeIn 0.5s ease',
        position: 'relative',
        zIndex: 1,
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '36px' }}>
          <div style={{
            width: '64px', height: '64px',
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            borderRadius: '16px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '28px', margin: '0 auto 16px',
            boxShadow: '0 0 30px rgba(59,130,246,0.4)',
            animation: 'float 3s ease-in-out infinite',
          }}>🛡️</div>
          <h1 style={{
            fontSize: '24px', fontWeight: '800',
            background: 'linear-gradient(135deg, #fff, #94a3b8)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '6px'
          }}>AI Proctor System</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
            Sign in to continue
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="error-banner" style={{ marginBottom: '20px' }}>
            ⚠️ {error}
          </div>
        )}

        {/* Username */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{
            color: 'var(--text-secondary)', fontSize: '12px',
            fontWeight: '600', display: 'block',
            marginBottom: '6px', textTransform: 'uppercase',
            letterSpacing: '0.06em'
          }}>Username</label>
          <input
            className="input-field"
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="Enter your username"
            onKeyDown={e => e.key === 'Enter' && handleLogin()}
          />
        </div>

        {/* Password */}
        <div style={{ marginBottom: '28px' }}>
          <label style={{
            color: 'var(--text-secondary)', fontSize: '12px',
            fontWeight: '600', display: 'block',
            marginBottom: '6px', textTransform: 'uppercase',
            letterSpacing: '0.06em'
          }}>Password</label>
          <input
            className="input-field"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Enter your password"
            onKeyDown={e => e.key === 'Enter' && handleLogin()}
          />
        </div>

        {/* Button */}
        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: '100%', padding: '13px',
            background: loading
              ? 'rgba(59,130,246,0.3)'
              : 'linear-gradient(135deg, #3b82f6, #2563eb)',
            color: '#fff', border: 'none', borderRadius: '10px',
            fontSize: '15px', fontWeight: '700', cursor: 'pointer',
            transition: 'all 0.2s ease',
            fontFamily: 'Inter, sans-serif',
            boxShadow: loading ? 'none' : '0 0 20px rgba(59,130,246,0.4)',
            display: 'flex', alignItems: 'center',
            justifyContent: 'center', gap: '8px',
          }}
        >
          {loading ? (
            <>
              <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }} />
              Signing in...
            </>
          ) : 'Sign In →'}
        </button>

        {/* Demo accounts */}
        <div style={{
          marginTop: '24px',
          padding: '16px',
          background: 'rgba(0,0,0,0.2)',
          borderRadius: '10px',
          border: '1px solid var(--border)',
        }}>
          <div style={{
            fontSize: '11px', color: 'var(--text-muted)',
            fontWeight: '700', textTransform: 'uppercase',
            letterSpacing: '0.06em', marginBottom: '8px'
          }}>Demo Accounts</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.8' }}>
            <span style={{ color: '#60a5fa' }}>👤 student1</span> / admin123 → Exam<br/>
            <span style={{ color: '#a78bfa' }}>🔑 admin</span> / admin123 → Dashboard
          </div>
        </div>
      </div>
    </div>
  );
}