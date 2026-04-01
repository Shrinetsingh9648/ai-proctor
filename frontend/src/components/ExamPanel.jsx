import React, { useState } from 'react';

const QUESTIONS = [
  { id:1, text:'What is the time complexity of binary search?', options:['O(1)','O(log n)','O(n)','O(n²)'], correct:1 },
  { id:2, text:'Which data structure uses LIFO order?', options:['Queue','Array','Stack','Linked List'], correct:2 },
  { id:3, text:'What does HTTP stand for?', options:['HyperText Transfer Protocol','High Transfer Text Process','Host Text Transmission Protocol','HyperText Transmission Process'], correct:0 },
];

export default function ExamPanel() {
  const [current, setCurrent]     = useState(0);
  const [selected, setSelected]   = useState({});
  const [submitted, setSubmitted] = useState(false);

  const q = QUESTIONS[current];

  if (submitted) {
    const score = QUESTIONS.filter(q => selected[q.id] === q.correct).length;
    return (
      <div className="exam">
        <div className="result-box">
          <div className="result-score">{score}/{QUESTIONS.length}</div>
          <div className="result-label">Exam submitted</div>
          <div className="result-sub">{score === QUESTIONS.length ? 'Perfect score!' : 'Good effort!'}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="exam">
      <div className="exam-header">
        <span>Question {current + 1} of {QUESTIONS.length}</span>
        <div className="progress-dots">
          {QUESTIONS.map((_, i) => (
            <div key={i} className={`dot ${i === current ? 'dot-active' : selected[QUESTIONS[i].id] !== undefined ? 'dot-done' : 'dot-inactive'}`} />
          ))}
        </div>
      </div>

      <p className="q-text">{q.text}</p>

      <div className="options">
        {q.options.map((opt, i) => (
          <button
            key={i}
            className={`option-btn ${selected[q.id] === i ? 'selected' : ''}`}
            onClick={() => setSelected(p => ({ ...p, [q.id]: i }))}
          >
            <span style={{ color:'#64748b', marginRight:'8px' }}>{String.fromCharCode(65+i)}.</span>
            {opt}
          </button>
        ))}
      </div>

      <button
        className="next-btn"
        disabled={selected[q.id] === undefined}
        onClick={() => current < QUESTIONS.length - 1 ? setCurrent(c => c+1) : setSubmitted(true)}
      >
        {current < QUESTIONS.length - 1 ? 'Next question →' : 'Submit exam'}
      </button>
    </div>
  );
}