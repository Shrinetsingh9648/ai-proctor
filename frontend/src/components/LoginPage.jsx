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
      // OAuth2 requires form data, not JSON
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res  = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || 'Login failed');
        setLoading(false);
        return;
      }

      // Save token to localStorage
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
      minHeight: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      background: '#0f1117',
    }}>
      <div style={{
        background: '#1e293b', borderRadius: '16px',
        padding: '40px', width: '100%', maxWidth: '400px',
      }}>
        {/* Logo / Title */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>🛡️</div>
          <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700' }}>
            AI Proctor System
          </h1>
          <p style={{ color: '#64748b', fontSize: '14px', marginTop: '4px' }}>
            Sign in to continue
          </p>
        </div>

        {/* Error */}
        {error && (
          <div style={{
            background: '#7f1d1d', border: '1px solid #991b1b',
            borderRadius: '8px', padding: '10px 14px',
            color: '#fca5a5', fontSize: '13px', marginBottom: '16px',
          }}>
            {error}
          </div>
        )}

        {/* Username */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{ color: '#94a3b8', fontSize: '13px', display: 'block', marginBottom: '6px' }}>
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="e.g. student1 or admin"
            onKeyDown={e => e.key === 'Enter' && handleLogin()}
            style={{
              width: '100%', padding: '10px 14px',
              background: '#0f172a', border: '1px solid #334155',
              borderRadius: '8px', color: '#f1f5f9', fontSize: '14px',
              outline: 'none', boxSizing: 'border-box',
            }}
          />
        </div>

        {/* Password */}
        <div style={{ marginBottom: '24px' }}>
          <label style={{ color: '#94a3b8', fontSize: '13px', display: 'block', marginBottom: '6px' }}>
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Enter password"
            onKeyDown={e => e.key === 'Enter' && handleLogin()}
            style={{
              width: '100%', padding: '10px 14px',
              background: '#0f172a', border: '1px solid #334155',
              borderRadius: '8px', color: '#f1f5f9', fontSize: '14px',
              outline: 'none', boxSizing: 'border-box',
            }}
          />
        </div>

        {/* Login button */}
        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: '100%', padding: '12px',
            background: loading ? '#1e3a5f' : '#2563eb',
            color: '#fff', border: 'none', borderRadius: '8px',
            fontSize: '15px', fontWeight: '600', cursor: 'pointer',
          }}
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>

        {/* Demo credentials hint */}
        <div style={{
          marginTop: '24px', padding: '12px',
          background: '#0f172a', borderRadius: '8px',
          fontSize: '12px', color: '#64748b',
        }}>
          <div style={{ marginBottom: '4px', color: '#94a3b8', fontWeight: '600' }}>
            Demo accounts:
          </div>
          <div>👤 student1 / admin123 → Exam view</div>
          <div>🔑 admin / admin123 → Admin dashboard</div>
        </div>
      </div>
    </div>
  );
}