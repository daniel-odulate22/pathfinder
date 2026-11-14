import { type FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { askPathfinder, detectFrame, getHistory } from "./services/pathfinderApi";
import { useSpeech } from "./hooks/useSpeech";
import type { Announcement, Detection } from "./types";

export default function App() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [running, setRunning] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("Start the camera to get a live description of the space around you.");
  const [detections, setDetections] = useState<Detection[]>([]);
  const [history, setHistory] = useState<Announcement[]>([]);
  const [cameraRatio, setCameraRatio] = useState("4 / 3");
  const speech = useSpeech();

  const refreshHistory = useCallback(() => { getHistory().then(setHistory).catch(() => undefined); }, []);
  const announce = useCallback((text: string) => { setAnswer(text); speech.speak(text); refreshHistory(); }, [speech.speak, refreshHistory]);

  useEffect(() => { refreshHistory(); }, [refreshHistory]);

  useEffect(() => {
    if (!running) return;
    let cancelled = false;
    let stream: MediaStream | undefined;
    let active = false;
    const capture = document.createElement("canvas");
    const wait = (ms: number) => new Promise(resolve => window.setTimeout(resolve, ms));
    async function runCamera() {
      try {
        if (!navigator.mediaDevices?.getUserMedia) throw new Error("Camera access is unavailable in this browser.");
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } }, audio: false });
        if (cancelled) { stream.getTracks().forEach(track => track.stop()); return; }
        const video = videoRef.current;
        if (!video) return;
        video.srcObject = stream;
        await video.play();
        setCameraRatio(video.videoWidth + " / " + video.videoHeight);
        active = true;
        while (!cancelled && active) {
          if (!video.videoWidth || !video.videoHeight) { await wait(250); continue; }
          capture.width = video.videoWidth; capture.height = video.videoHeight;
          capture.getContext("2d")?.drawImage(video, 0, 0);
          const frame = await new Promise<Blob | null>(resolve => capture.toBlob(resolve, "image/jpeg", 0.72));
          if (!frame) throw new Error("Could not capture a camera frame.");
          const data = await detectFrame(frame);
          if (cancelled) break;
          setDetections(data.detections);
          drawDetections(data.detections, canvasRef.current, video.videoWidth, video.videoHeight);
          if (data.announce && data.description) announce(data.description);
          await wait(450);
        }
      } catch (cause) {
        if (!cancelled) { setError(cause instanceof Error ? cause.message : String(cause)); setRunning(false); }
      }
    }
    void runCamera();
    return () => { cancelled = true; active = false; stream?.getTracks().forEach(track => track.stop()); speech.stopSpeaking(); };
  }, [running, announce, speech.stopSpeaking]);

  async function ask(text: string) {
    const trimmed = text.trim();
    if (!trimmed || busy) return;
    setBusy(true); setError(""); setQuestion("");
    try { const result = await askPathfinder(trimmed); announce(result.answer); }
    catch (cause) { setError(cause instanceof Error ? cause.message : String(cause)); }
    finally { setBusy(false); }
  }

  function submit(event: FormEvent) { event.preventDefault(); void ask(question); }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#home" aria-label="Pathfinder home"><span className="brand-mark">P</span><span>pathfinder<small>SEE YOUR SURROUNDINGS</small></span></a>
        <div className="topbar-right"><span className={"status-pill " + (running ? "is-live" : "") }><i />{running ? "LIVE SESSION" : "SESSION PAUSED"}</span><button className="quiet-button" onClick={speech.toggleMute} aria-pressed={speech.muted}>{speech.muted ? "Sound off" : "Sound on"}</button></div>
      </header>
      <section className="workspace" id="home">
        <div className="main-column">
          <div className="section-heading"><div><p className="eyebrow">YOUR POINT OF VIEW</p><h1>Understand the space around you.</h1><p className="subheading">A live picture of your surroundings, translated into words.</p></div><span className="session-index">01 <b>/</b> LIVE VIEW</span></div>
          <section className="camera-card" aria-label="Live camera workspace">
            <div className="camera-toolbar"><span><i className={running ? "live-dot" : "idle-dot"} />{running ? "Camera active" : "Camera ready"}</span><span>{running ? detections.length + " objects in view" : "Waiting for camera"}</span></div>
            <div className="camera-stage" style={{ aspectRatio: cameraRatio }}>
              <video ref={videoRef} muted playsInline aria-label="Live camera preview" />
              <canvas ref={canvasRef} aria-hidden="true" />
              {!running && <div className="camera-placeholder"><div className="aperture"><span /></div><strong>Your surroundings, in focus.</strong><p>Start the camera when you are ready.</p></div>}
              {running && <div className="frame-corner corner-tl" />}{running && <div className="frame-corner corner-tr" />}{running && <div className="frame-corner corner-bl" />}{running && <div className="frame-corner corner-br" />}
            </div>
            <div className="camera-footer"><span>CAMERA FEED <b>·</b> ON-DEVICE PREVIEW</span><button className={running ? "stop-button" : "start-button"} onClick={() => { setError(""); setRunning(value => !value); }}>{running ? "Stop camera" : "Start camera"}<span>{running ? "Ⅱ" : "↗"}</span></button></div>
          </section>
          <div className="safety-line"><span>ⓘ</span><p>Pathfinder is an experimental awareness aid, not a navigation or collision-avoidance system. It can miss or misidentify objects and does not replace a white cane, guide dog, or mobility training.</p></div>
        </div>
        <aside className="insight-column">
          <section className="observation-panel"><div className="panel-heading"><div><p className="eyebrow">02 / SCENE NOTES</p><h2>What I notice</h2></div><span className="panel-symbol">◉</span></div>
            <div className="answer-block" aria-live="polite"><span className="tiny-label">LATEST OBSERVATION</span><p>{answer}</p></div>
            <div className="detected-heading"><span className="tiny-label">IN THE FRAME</span><span>{detections.length.toString().padStart(2, "0")}</span></div>
            {detections.length ? <ul className="detection-list">{detections.slice(0, 8).map((item, index) => <li key={item.class_name + item.position + index}><span className="detection-name"><i />{item.class_name.replaceAll("_", " ")}</span><span className="detection-position">{item.position}</span></li>)}</ul> : <p className="empty-state">{running ? "Nothing detected just yet. Keep the camera steady." : "Detected objects will appear here."}</p>}
          </section>
          <section className="ask-panel"><p className="eyebrow">03 / ASK ABOUT THIS VIEW</p><h2>Curious about something?</h2><p className="ask-description">Ask a question about what the camera can currently see.</p>
            <form onSubmit={submit} className="question-form"><label className="sr-only" htmlFor="question">Ask Pathfinder a question</label><input id="question" value={question} onChange={event => setQuestion(event.target.value)} maxLength={200} placeholder="Where is the chair?" /><button type="submit" disabled={busy || !question.trim()} aria-label="Send question">↗</button></form>
            <div className="ask-actions"><button className="voice-button" disabled={!speech.supported} onClick={() => speech.listen(text => void ask(text), setError)}><span>◖</span> Ask by voice</button><button className="read-button" onClick={() => void ask("Read the text")}>Read text <span>↗</span></button></div>
            {!speech.supported && <p className="support-note">Voice input is unavailable in this browser. You can still type a question.</p>}
          </section>
          <section className="history-panel"><div className="panel-heading"><div><p className="eyebrow">04 / RECENT ACTIVITY</p><h2>Earlier observations</h2></div><button className="text-button" onClick={refreshHistory}>Refresh ↻</button></div>
            {history.length ? <ol className="history-list">{history.slice(0, 4).map(entry => <li key={entry.id}><time>{new Date(entry.created_at.replace(" ", "T") + "Z").toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time><span>{entry.text}</span></li>)}</ol> : <p className="empty-state">Your recent observations will collect here.</p>}
          </section>
        </aside>
      </section>
      {error && <div className="error-toast" role="alert"><span>{error}</span><button onClick={() => setError("")} aria-label="Dismiss error">×</button></div>}
      <footer className="app-footer"><span>PATHFINDER <b>·</b> BUILT FOR A MORE UNDERSTANDABLE WORLD</span><span>EXPERIMENTAL BUILD 0.2</span></footer>
    </main>
  );
}

function drawDetections(items: Detection[], canvas: HTMLCanvasElement | null, width: number, height: number) {
  if (!canvas) return;
  canvas.width = width; canvas.height = height;
  const context = canvas.getContext("2d");
  if (!context) return;
  context.lineWidth = Math.max(2, width / 500);
  context.font = "600 " + Math.max(13, width / 65) + "px system-ui";
  context.strokeStyle = "#d7ff62"; context.fillStyle = "#d7ff62";
  for (const item of items) {
    const [x1, y1, x2, y2] = item.box;
    context.strokeRect(x1, y1, x2 - x1, y2 - y1);
    const label = item.class_name + " · " + item.position;
    const y = Math.max(20, y1 - 9);
    context.fillText(label, x1, y);
  }
}