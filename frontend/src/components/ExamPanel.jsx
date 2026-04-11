import React, { useState, useEffect, useCallback } from 'react';

const EXAM_DURATION = 45 * 60;

export default function ExamPanel({ token }) {
  const [phase, setPhase]         = useState('start');
  const [session, setSession]     = useState(null);
  const [questions, setQuestions] = useState([]);
  const [current, setCurrent]     = useState(0);
  const [answers, setAnswers]     = useState({});
  const [timeLeft, setTimeLeft]   = useState(EXAM_DURATION);
  const [result, setResult]       = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);

  // Timer
  useEffect(() => {
    if (phase !== 'exam') return;
    if (timeLeft <= 0) { submitExam(); return; }
    const t = setInterval(() => setTimeLeft(p => p - 1), 1000);
    return () => clearInterval(t);
  }, [phase, timeLeft]);

  function formatTime(secs) {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }

  async function startExam() {
    setLoading(true);
    setError(null);
    try {
      // Step 1 — start session
      const res = await fetch('http://localhost:8000/exam/start', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!res.ok) {
        const err = await res.json();
        setError(`Failed to start: ${err.detail}`);
        setLoading(false);
        return;
      }

      const sess = await res.json();
      console.log('Session created:', sess);

      if (!sess.id) {
        setError('No session ID returned');
        setLoading(false);
        return;
      }

      setSession(sess);

      // Step 2 — get questions
      const qRes = await fetch(`http://localhost:8000/exam/questions/${sess.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!qRes.ok) {
        const err = await qRes.json();
        setError(`Failed to get questions: ${err.detail}`);
        setLoading(false);
        return;
      }

      const data = await qRes.json();
      console.log('Questions received:', data);

      const qs = data.questions || [];

      if (qs.length === 0) {
        setError('No questions in database! Ask admin to add questions first.');
        setLoading(false);
        return;
      }

      // Set questions FIRST, then change phase
      setQuestions(qs);
      setLoading(false);
      setPhase('exam');

    } catch (e) {
      console.error('Start exam error:', e);
      setError(`Error: ${e.message}`);
      setLoading(false);
    }
  }

 const submitExam = useCallback(async () => {
    if (!session) return;
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/exam/submit', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: session.id,
          answers: answers
        })
      });

      if (!res.ok) {
        const err = await res.json();
        setError(`Submit failed: ${err.detail}`);
        setLoading(false);
        return;
      }

      const data = await res.json();
      console.log('Result:', data);
      setResult(data);
      setLoading(false);
      setPhase('result');

    } catch (e) {
      console.error(e);
      setError(`Submit failed: ${e.message}`);
      setLoading(false);
    }
  }, [session, answers, token]);
  // ── START SCREEN ──────────────────────────────────────────────
  if (phase === 'start') return (
    <div className="exam" style={{
      justifyContent: 'center', alignItems: 'center', minHeight: '400px'
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📝</div>
        <h2 style={{ color: '#fff', marginBottom: '8px' }}>Ready to start?</h2>
        <p style={{ color: '#64748b', marginBottom: '8px' }}>
          10 questions · 45 minutes · AI monitored
        </p>
        <p style={{ color: '#f87171', fontSize: '13px', marginBottom: '24px' }}>
          ⚠️ Do not switch tabs or leave this window
        </p>
        {error && (
          <div className="alert-red" style={{ marginBottom: '16px' }}>
            {error}
          </div>
        )}
        <button
          className="next-btn"
          onClick={startExam}
          disabled={loading}
          style={{ padding: '12px 32px', fontSize: '15px' }}
        >
          {loading ? 'Loading...' : 'Start Exam →'}
        </button>
      </div>
    </div>
  );

  // ── RESULT SCREEN ─────────────────────────────────────────────
  if (phase === 'result' && result) return (
    <div className="exam">
      <div className="result-box">
        <div style={{
          fontSize: '64px', fontWeight: '700',
          color: result.percentage >= 60 ? '#4ade80' : '#f87171'
        }}>
          {result.score}/{result.total}
        </div>
        <div style={{
          fontSize: '32px', fontWeight: '600',
          color: result.percentage >= 60 ? '#4ade80' : '#f87171'
        }}>
          {result.percentage}%
        </div>
        <div className="result-label">
          {result.percentage >= 90 ? '🏆 Excellent!' :
           result.percentage >= 75 ? '🎉 Great job!' :
           result.percentage >= 60 ? '✅ Passed!' :
           '❌ Failed — Try again'}
        </div>
        <div className="result-sub">Exam submitted successfully</div>
      </div>
    </div>
  );

  // ── LOADING SCREEN ────────────────────────────────────────────
  if (phase === 'exam' && questions.length === 0) return (
    <div className="exam" style={{
      alignItems: 'center', justifyContent: 'center', minHeight: '300px'
    }}>
      <div style={{ textAlign: 'center', color: '#64748b' }}>
        <div style={{ fontSize: '32px', marginBottom: '8px' }}>⏳</div>
        <div>Loading questions...</div>
      </div>
    </div>
  );

  const q = questions[current];

  if (!q) return null;

  const isLowTime = timeLeft < 5 * 60;

  // ── EXAM SCREEN ───────────────────────────────────────────────
  return (
    <div className="exam">
      {/* Header */}
      <div className="exam-header">
        <span>Question {current + 1} of {questions.length}</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: isLowTime ? '#7f1d1d' : '#1e293b',
            color: isLowTime ? '#fca5a5' : '#94a3b8',
            padding: '4px 10px', borderRadius: '6px',
            fontSize: '14px', fontWeight: '600',
            border: isLowTime ? '1px solid #991b1b' : 'none'
          }}>
            ⏱️ {formatTime(timeLeft)}
          </div>
          <div className="progress-dots">
            {questions.map((_, i) => (
              <div key={i} className={`dot ${
                i === current ? 'dot-active' :
                answers[questions[i]?.id] ? 'dot-done' :
                'dot-inactive'
              }`} />
            ))}
          </div>
        </div>
      </div>

      {/* Subject badge */}
      <div style={{
        display: 'inline-block',
        background: '#1e3a5f', color: '#60a5fa',
        padding: '3px 10px', borderRadius: '999px',
        fontSize: '11px', fontWeight: '500'
      }}>
        {q.subject} · {q.difficulty}
      </div>

      {/* Question */}
      <p className="q-text">{q.question_text}</p>

      {/* Options */}
      <div className="options">
        {['A', 'B', 'C', 'D'].map(letter => {
          const optionKey = `option_${letter.toLowerCase()}`;
          const isSelected = answers[q.id] === letter;
          return (
            <button
              key={letter}
              className={`option-btn ${isSelected ? 'selected' : ''}`}
              onClick={() => setAnswers(p => ({ ...p, [q.id]: letter }))}
            >
              <span style={{ color: '#64748b', marginRight: '8px' }}>
                {letter}.
              </span>
              {q[optionKey]}
            </button>
          );
        })}
      </div>

      {/* Navigation */}
      <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
        {current > 0 && (
          <button
            className="next-btn"
            onClick={() => setCurrent(c => c - 1)}
            style={{ background: '#1e293b', flex: 1 }}
          >
            ← Previous
          </button>
        )}
        {current < questions.length - 1 ? (
          <button
            className="next-btn"
            onClick={() => setCurrent(c => c + 1)}
            style={{ flex: 1 }}
          >
            Next →
          </button>
        ) : (
          <button
            className="next-btn"
            onClick={submitExam}
            disabled={loading}
            style={{ flex: 1, background: '#16a34a' }}
          >
            {loading ? 'Submitting...' : '✅ Submit Exam'}
          </button>
        )}
      </div>

      {/* Answered count */}
      <div style={{ textAlign: 'center', fontSize: '12px', color: '#64748b' }}>
        {Object.keys(answers).length} of {questions.length} answered
      </div>
    </div>
  );
}