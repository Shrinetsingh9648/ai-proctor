import React, { useState, useEffect } from 'react';

export default function QuestionManager({ token }) {
  const [questions, setQuestions] = useState([]);
  const [showForm, setShowForm]   = useState(false);
  const [editing, setEditing]     = useState(null);
  const [loading, setLoading]     = useState(false);
  const [form, setForm] = useState({
    subject: '', question_text: '',
    option_a: '', option_b: '', option_c: '', option_d: '',
    correct_answer: 'A', difficulty: 'medium'
  });

  const BACKEND = process.env.REACT_APP_BACKEND_URL || 'localhost:8000';
  const API = `http://localhost:8000`;

  async function fetchQuestions() {
    const res = await fetch(`${API}/questions`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    setQuestions(Array.isArray(data) ? data : []);
  }

  useEffect(() => { fetchQuestions(); }, []);

  async function saveQuestion() {
    setLoading(true);
    const url = editing ? `${API}/questions/${editing}` : `${API}/questions`;
    const method = editing ? 'PUT' : 'POST';
    await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form)
    });
    setShowForm(false);
    setEditing(null);
    resetForm();
    fetchQuestions();
    setLoading(false);
  }

  async function deleteQuestion(id) {
    if (!window.confirm('Delete this question?')) return;
    await fetch(`${API}/questions/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    fetchQuestions();
  }

  function editQuestion(q) {
    setForm({
      subject: q.subject, question_text: q.question_text,
      option_a: q.option_a, option_b: q.option_b,
      option_c: q.option_c, option_d: q.option_d,
      correct_answer: q.correct_answer, difficulty: q.difficulty
    });
    setEditing(q.id);
    setShowForm(true);
  }

  function resetForm() {
    setForm({
      subject: '', question_text: '',
      option_a: '', option_b: '', option_c: '', option_d: '',
      correct_answer: 'A', difficulty: 'medium'
    });
  }

  const inputStyle = {
    width: '100%', padding: '8px 12px',
    background: '#0f172a', border: '1px solid #334155',
    borderRadius: '6px', color: '#f1f5f9',
    fontSize: '13px', boxSizing: 'border-box',
    marginBottom: '8px'
  };

  return (
    <div className="app">
      <div className="topbar">
        <div>
          <div className="topbar-title">Question Bank</div>
          <div className="topbar-sub">{questions.length} questions total</div>
        </div>
        <button
          onClick={() => { resetForm(); setEditing(null); setShowForm(true); }}
          style={{
            background: '#2563eb', color: '#fff', border: 'none',
            padding: '8px 16px', borderRadius: '8px',
            cursor: 'pointer', fontSize: '13px'
          }}
        >
          + Add Question
        </button>
      </div>

      {/* Add/Edit Form */}
      {showForm && (
        <div style={{
          background: '#1e293b', borderRadius: '12px',
          padding: '20px', marginBottom: '24px'
        }}>
          <h3 style={{ color: '#fff', marginBottom: '16px' }}>
            {editing ? 'Edit Question' : 'Add New Question'}
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <div>
              <label style={{ color: '#94a3b8', fontSize: '12px' }}>Subject</label>
              <input style={inputStyle} value={form.subject}
                onChange={e => setForm(p => ({...p, subject: e.target.value}))}
                placeholder="e.g. Data Structures" />
            </div>
            <div>
              <label style={{ color: '#94a3b8', fontSize: '12px' }}>Difficulty</label>
              <select style={inputStyle} value={form.difficulty}
                onChange={e => setForm(p => ({...p, difficulty: e.target.value}))}>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
          </div>

          <label style={{ color: '#94a3b8', fontSize: '12px' }}>Question</label>
          <textarea style={{...inputStyle, height: '80px', resize: 'vertical'}}
            value={form.question_text}
            onChange={e => setForm(p => ({...p, question_text: e.target.value}))}
            placeholder="Enter your question here..." />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            {['a','b','c','d'].map(opt => (
              <div key={opt}>
                <label style={{ color: '#94a3b8', fontSize: '12px' }}>
                  Option {opt.toUpperCase()}
                </label>
                <input style={inputStyle}
                  value={form[`option_${opt}`]}
                  onChange={e => setForm(p => ({...p, [`option_${opt}`]: e.target.value}))}
                  placeholder={`Option ${opt.toUpperCase()}`} />
              </div>
            ))}
          </div>

          <label style={{ color: '#94a3b8', fontSize: '12px' }}>Correct Answer</label>
          <select style={{...inputStyle, width: '200px'}}
            value={form.correct_answer}
            onChange={e => setForm(p => ({...p, correct_answer: e.target.value}))}>
            <option value="A">A</option>
            <option value="B">B</option>
            <option value="C">C</option>
            <option value="D">D</option>
          </select>

          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
            <button onClick={saveQuestion} disabled={loading}
              style={{
                background: '#2563eb', color: '#fff', border: 'none',
                padding: '8px 20px', borderRadius: '6px', cursor: 'pointer'
              }}>
              {loading ? 'Saving...' : editing ? 'Update' : 'Add Question'}
            </button>
            <button onClick={() => setShowForm(false)}
              style={{
                background: '#1e293b', color: '#94a3b8', border: '1px solid #334155',
                padding: '8px 20px', borderRadius: '6px', cursor: 'pointer'
              }}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Questions Table */}
      <div style={{ background: '#1e293b', borderRadius: '12px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#0f172a' }}>
              {['#', 'Subject', 'Question', 'Difficulty', 'Answer', 'Actions'].map(h => (
                <th key={h} style={{
                  padding: '10px 16px', textAlign: 'left',
                  fontSize: '11px', color: '#64748b',
                  textTransform: 'uppercase'
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {questions.map((q, i) => (
              <tr key={q.id} style={{ borderBottom: '1px solid #0f172a' }}>
                <td style={{ padding: '10px 16px', color: '#475569', fontSize: '13px' }}>
                  #{q.id}
                </td>
                <td style={{ padding: '10px 16px' }}>
                  <span style={{
                    background: '#1e3a5f', color: '#60a5fa',
                    padding: '2px 8px', borderRadius: '999px', fontSize: '11px'
                  }}>{q.subject}</span>
                </td>
                <td style={{
                  padding: '10px 16px', color: '#cbd5e1',
                  fontSize: '13px', maxWidth: '300px',
                  overflow: 'hidden', textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {q.question_text}
                </td>
                <td style={{ padding: '10px 16px' }}>
                  <span style={{
                    background: q.difficulty === 'easy' ? '#14532d' :
                                q.difficulty === 'medium' ? '#713f12' : '#7f1d1d',
                    color: q.difficulty === 'easy' ? '#86efac' :
                           q.difficulty === 'medium' ? '#fde68a' : '#fca5a5',
                    padding: '2px 8px', borderRadius: '999px', fontSize: '11px'
                  }}>{q.difficulty}</span>
                </td>
                <td style={{
                  padding: '10px 16px', color: '#4ade80',
                  fontSize: '13px', fontWeight: '700'
                }}>
                  {q.correct_answer}
                </td>
                <td style={{ padding: '10px 16px' }}>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button onClick={() => editQuestion(q)}
                      style={{
                        background: '#1e3a5f', color: '#60a5fa',
                        border: 'none', padding: '4px 10px',
                        borderRadius: '4px', cursor: 'pointer', fontSize: '12px'
                      }}>Edit</button>
                    <button onClick={() => deleteQuestion(q.id)}
                      style={{
                        background: '#7f1d1d', color: '#fca5a5',
                        border: 'none', padding: '4px 10px',
                        borderRadius: '4px', cursor: 'pointer', fontSize: '12px'
                      }}>Delete</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {questions.length === 0 && (
          <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
            No questions yet. Click "Add Question" to start!
          </div>
        )}
      </div>
    </div>
  );
}