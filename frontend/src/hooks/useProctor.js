//import { useState, useEffect, useRef, useCallback } from 'react';
//
//const WS_URL = 'ws://localhost:8000/ws/proctor';
//const FRAME_INTERVAL_MS = 500;
//
//const DEFAULT_RESULT = {
//  face_count: 0,
//  looking_direction: 'connecting...',
//  phone_detected: false,
//  look_away_secs: 0,
//  suspicion_score: 0,
//  events: [],
//};
//
//export function useProctor(videoRef) {
//  const [result, setResult]       = useState(DEFAULT_RESULT);
//  const [connected, setConnected] = useState(false);
//  const [error, setError]         = useState(null);
//
//  const wsRef       = useRef(null);
//  const canvasRef   = useRef(null);
//  const intervalRef = useRef(null);
//
//  useEffect(() => {
//    canvasRef.current = document.createElement('canvas');
//    canvasRef.current.width  = 480;
//    canvasRef.current.height = 360;
//  }, []);
//
//  const sendFrame = useCallback(() => {
//    const video  = videoRef.current;
//    const canvas = canvasRef.current;
//    const ws     = wsRef.current;
//    if (!video || !canvas || !ws) return;
//    if (ws.readyState !== WebSocket.OPEN) return;
//    if (video.readyState < 2) return;
//    const ctx = canvas.getContext('2d');
//    ctx.drawImage(video, 0, 0, 480, 360);
//    ws.send(canvas.toDataURL('image/jpeg', 0.7));
//  }, [videoRef]);
//
//  useEffect(() => {
//    const ws = new WebSocket(WS_URL);
//    wsRef.current = ws;
//
//    ws.onopen = () => {
//      setConnected(true);
//      setError(null);
//      intervalRef.current = setInterval(sendFrame, FRAME_INTERVAL_MS);
//    };
//    ws.onmessage = (e) => {
//      try { setResult(JSON.parse(e.data)); }
//      catch {}
//    };
//    ws.onerror = () => {
//      setError('Cannot connect to backend. Is the server running on port 8000?');
//      setConnected(false);
//    };
//    ws.onclose = () => {
//      setConnected(false);
//      clearInterval(intervalRef.current);
//    };
//    return () => {
//      clearInterval(intervalRef.current);
//      ws.close();
//    };
//  }, [sendFrame]);
//
//  return { result, connected, error };
//}



//import { useState, useEffect, useRef, useCallback } from 'react';
//
//const FRAME_INTERVAL_MS = 500;
//
//const DEFAULT_RESULT = {
//  face_count: 0,
//  looking_direction: 'connecting...',
//  phone_detected: false,
//  look_away_secs: 0,
//  suspicion_score: 0,
//  events: [],
//};
//
//export function useProctor(videoRef, token) {
//  const [result, setResult]       = useState(DEFAULT_RESULT);
//  const [connected, setConnected] = useState(false);
//  const [error, setError]         = useState(null);
//
//  const wsRef       = useRef(null);
//  const canvasRef   = useRef(null);
//  const intervalRef = useRef(null);
//
//  useEffect(() => {
//    canvasRef.current = document.createElement('canvas');
//    canvasRef.current.width  = 480;
//    canvasRef.current.height = 360;
//  }, []);
//
//  const sendFrame = useCallback(() => {
//    const video  = videoRef.current;
//    const canvas = canvasRef.current;
//    const ws     = wsRef.current;
//    if (!video || !canvas || !ws) return;
//    if (ws.readyState !== WebSocket.OPEN) return;
//    if (video.readyState < 2) return;
//    const ctx = canvas.getContext('2d');
//    ctx.drawImage(video, 0, 0, 480, 360);
//    ws.send(canvas.toDataURL('image/jpeg', 0.7));
//  }, [videoRef]);
//
//  useEffect(() => {
//    // Pass token as query param so backend knows who this is
//    const wsUrl = `ws://localhost:8000/ws/proctor?token=${token || ''}`;
//    const ws    = new WebSocket(wsUrl);
//    wsRef.current = ws;
//
//    ws.onopen = () => {
//      setConnected(true);
//      setError(null);
//      intervalRef.current = setInterval(sendFrame, FRAME_INTERVAL_MS);
//    };
//    ws.onmessage = (e) => {
//      try { setResult(JSON.parse(e.data)); } catch {}
//    };
//    ws.onerror = () => {
//      setError('Cannot connect to backend. Is the server running on port 8000?');
//      setConnected(false);
//    };
//    ws.onclose = () => {
//      setConnected(false);
//      clearInterval(intervalRef.current);
//    };
//    return () => {
//      clearInterval(intervalRef.current);
//      ws.close();
//    };
//  }, [sendFrame, token]);
//
//  return { result, connected, error };
//}


import { useState, useEffect, useRef, useCallback } from 'react';

const FRAME_INTERVAL_MS = 500;

const DEFAULT_RESULT = {
  face_count: 0,
  looking_direction: 'connecting...',
  phone_detected: false,
  look_away_secs: 0,
  suspicion_score: 0,
  events: [],
  tab_switched: false,
  tab_switch_count: 0,
};

export function useProctor(videoRef, token) {
  const [result, setResult]           = useState(DEFAULT_RESULT);
  const [connected, setConnected]     = useState(false);
  const [error, setError]             = useState(null);
  const [tabSwitchCount, setTabSwitchCount] = useState(0);
  const [tabWarning, setTabWarning]   = useState(false);

  const wsRef       = useRef(null);
  const canvasRef   = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    canvasRef.current = document.createElement('canvas');
    canvasRef.current.width  = 480;
    canvasRef.current.height = 360;
  }, []);

  // ── Tab switching detection ───────────────────────────────────
  useEffect(() => {
    function handleVisibilityChange() {
      if (document.hidden) {
        // Student switched away from tab
        setTabSwitchCount(prev => prev + 1);
        setTabWarning(true);

        // Send tab_switch event to backend via WebSocket
        const ws = wsRef.current;
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'tab_switch' }));
        }

        // Hide warning after 4 seconds when they come back
        setTimeout(() => setTabWarning(false), 4000);
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  const sendFrame = useCallback(() => {
    const video  = videoRef.current;
    const canvas = canvasRef.current;
    const ws     = wsRef.current;
    if (!video || !canvas || !ws) return;
    if (ws.readyState !== WebSocket.OPEN) return;
    if (video.readyState < 2) return;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, 480, 360);
    ws.send(canvas.toDataURL('image/jpeg', 0.7));
  }, [videoRef]);

  useEffect(() => {
//    const wsUrl = `ws://localhost:8000/ws/proctor?token=${token || ''}`;
const BACKEND = process.env.REACT_APP_BACKEND_URL || 'localhost:8000';
const wsUrl = `wss://${BACKEND}/ws/proctor?token=${token || ''}`;

    const ws    = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      setError(null);
      intervalRef.current = setInterval(sendFrame, FRAME_INTERVAL_MS);
    };
    ws.onmessage = (e) => {
      try { setResult(JSON.parse(e.data)); } catch {}
    };
    ws.onerror = () => {
      setError('Cannot connect to backend. Is the server running on port 8000?');
      setConnected(false);
    };
    ws.onclose = () => {
      setConnected(false);
      clearInterval(intervalRef.current);
    };
    return () => {
      clearInterval(intervalRef.current);
      ws.close();
    };
  }, [sendFrame, token]);

  return { result, connected, error, tabSwitchCount, tabWarning };
}

