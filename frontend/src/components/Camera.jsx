import React, { useEffect } from 'react';

export default function Camera({ videoRef, isSuspicious }) {
  useEffect(() => {
    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 480, height: 360 } });
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (err) {
        console.error('Camera error:', err);
      }
    }
    startCamera();
  }, [videoRef]);

  return (
    <div className="camera-wrap">
      <video ref={videoRef} autoPlay muted playsInline />
      {isSuspicious && <div className="camera-alert" />}
      <div className="live-badge">
        <div className="live-dot" />
        <span className="live-text">LIVE</span>
      </div>
    </div>
  );
}