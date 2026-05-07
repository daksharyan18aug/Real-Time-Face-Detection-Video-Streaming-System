import React, { useState } from "react";
import VideoStream from "./components/VideoStream";
import ROITable from "./components/ROITable";
import "./App.css";

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎯 Real-Time Face Detection</h1>
        <p>Live face detection powered by MediaPipe + Pillow</p>
        {sessionId && (
          <p className="session-id">
            Session: <code>{sessionId}</code>
          </p>
        )}
      </header>

      <main className="app-main">
        <section className="video-section">
          <VideoStream
            onSessionStart={setSessionId}
            onStreamingChange={setIsStreaming}
          />
        </section>

        <section className="roi-section">
          <ROITable sessionId={sessionId} isStreaming={isStreaming} />
        </section>
      </main>
    </div>
  );
}

export default App;