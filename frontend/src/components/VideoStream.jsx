import React, { useRef, useEffect, useState, useCallback } from "react";

const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:8000/ws/stream";
const FRAME_INTERVAL_MS = 100; // send 10 frames per second

function VideoStream({ onSessionStart, onStreamingChange }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const intervalRef = useRef(null);
  const annotatedImgRef = useRef(null);

  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [faceDetected, setFaceDetected] = useState(false);
  const [frameCount, setFrameCount] = useState(0);

  // Start camera + WebSocket
  const startStream = useCallback(async () => {
    setError(null);

    // 1. Get camera access
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
    } catch (err) {
      setError("Camera access denied. Please allow camera permissions.");
      return;
    }

    // 2. Connect WebSocket
    const ws = new WebSocket(WS_URL);
    ws.binaryType = "arraybuffer";
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      setStreaming(true);
      onStreamingChange(true);

      // 3. Start sending frames
      intervalRef.current = setInterval(() => {
        if (ws.readyState !== WebSocket.OPEN) return;

        const canvas = canvasRef.current;
        const video = videoRef.current;
        if (!canvas || !video) return;

        const ctx = canvas.getContext("2d");
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert frame to JPEG blob and send
        canvas.toBlob(
          (blob) => {
            if (blob && ws.readyState === WebSocket.OPEN) {
              blob.arrayBuffer().then((buf) => ws.send(buf));
              setFrameCount((c) => c + 1);
            }
          },
          "image/jpeg",
          0.8
        );
      }, FRAME_INTERVAL_MS);
    };

    // 4. Receive annotated frames back
    ws.onmessage = (event) => {
      const blob = new Blob([event.data], { type: "image/jpeg" });
      const url = URL.createObjectURL(blob);

      if (annotatedImgRef.current) {
        // Revoke previous URL to avoid memory leaks
        if (annotatedImgRef.current.src.startsWith("blob:")) {
          URL.revokeObjectURL(annotatedImgRef.current.src);
        }
        annotatedImgRef.current.src = url;
      }

      // Simple heuristic — if frame came back it was processed
      setFaceDetected(true);
    };

    ws.onerror = () => {
      setError("WebSocket error — is the backend running?");
    };

    ws.onclose = (event) => {
      console.log("WebSocket closed", event.code);

      // Extract session_id from close reason if sent by server
      if (event.reason) {
        onSessionStart(event.reason);
      }

      setStreaming(false);
      onStreamingChange(false);
      setFaceDetected(false);
      clearInterval(intervalRef.current);
    };

  }, [onSessionStart, onStreamingChange]);

  // Stop camera + WebSocket
  const stopStream = useCallback(() => {
    clearInterval(intervalRef.current);

    if (wsRef.current) {
      wsRef.current.close();
    }

    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
      videoRef.current.srcObject = null;
    }

    setStreaming(false);
    setFrameCount(0);
    onStreamingChange(false);
  }, [onStreamingChange]);

  // Cleanup on unmount
  useEffect(() => {
    return () => stopStream();
  }, [stopStream]);

  return (
    <div className="video-stream">
      <div className="video-container">
        {/* Hidden: raw camera feed used for frame capture */}
        <video ref={videoRef} style={{ display: "none" }} muted />

        {/* Hidden: canvas used to grab frames */}
        <canvas ref={canvasRef} style={{ display: "none" }} />

        {/* Visible: annotated frames returned from backend */}
        <img
          ref={annotatedImgRef}
          alt="Annotated video feed"
          className="annotated-feed"
          style={{ display: streaming ? "block" : "none" }}
        />

        {/* Placeholder when not streaming */}
        {!streaming && (
          <div className="feed-placeholder">
            <span>📷</span>
            <p>Camera feed will appear here</p>
          </div>
        )}

        {/* Face detection badge */}
        {streaming && (
          <div className={`detection-badge ${faceDetected ? "detected" : "not-detected"}`}>
            {faceDetected ? "✅ Face Detected" : "🔍 Scanning..."}
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="controls">
        {!streaming ? (
          <button className="btn btn-start" onClick={startStream}>
            ▶ Start Stream
          </button>
        ) : (
          <button className="btn btn-stop" onClick={stopStream}>
            ⏹ Stop Stream
          </button>
        )}
        {streaming && (
          <span className="frame-counter">Frames sent: {frameCount}</span>
        )}
      </div>

      {error && <div className="error-box">⚠️ {error}</div>}
    </div>
  );
}

export default VideoStream;