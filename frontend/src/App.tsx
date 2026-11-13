import { type FormEvent, useEffect, useRef, useState } from "react";

type Detection = {
  class_name: string;
  position: string;
  attention: string;
  confidence: number;
  box: [number, number, number, number];
};
type Entry = { id: number; created_at: string; text: string };

// Not in TypeScript's DOM lib; Chrome and Safari only, so the mic button hides elsewhere.
const Recognition =
  (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition;

export default function App() {
  const video = useRef<HTMLVideoElement>(null);
  const overlay = useRef<HTMLCanvasElement>(null);
  const muted = useRef(false);
  const [running, setRunning] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [spoken, setSpoken] = useState("");
  const [error, setError] = useState("");
  const [history, setHistory] = useState<Entry[]>([]);
  const [question, setQuestion] = useState("");

  const loadHistory = () =>
    fetch("/api/history")
      .then((res) => res.json())
      .then(setHistory)
      .catch(() => {});

  function say(text: string) {
    setSpoken(text);
    loadHistory();
    if (muted.current) return;
    speechSynthesis.cancel(); // latest message wins, like the desktop narrator
    speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  }

  function draw(detections: Detection[]) {
    const canvas = overlay.current!;
    const { videoWidth: w, videoHeight: h } = video.current!;
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d")!;
    ctx.lineWidth = 3;
    ctx.font = "bold 18px system-ui";
    ctx.strokeStyle = "rgba(255,255,255,0.4)";
    for (const x of [w / 3, (w * 2) / 3]) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    ctx.strokeStyle = ctx.fillStyle = "#ffd400";
    for (const d of detections) {
      const [x1, y1, x2, y2] = d.box;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      ctx.fillText(`${d.class_name} | ${d.position} | ${d.attention}`, x1, Math.max(20, y1 - 8));
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    if (!running) return;
    let stop = false;
    let stream: MediaStream | undefined;
    const grab = document.createElement("canvas");

    (async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment" },
        });
        if (stop) return stream.getTracks().forEach((t) => t.stop());
        const v = video.current!;
        v.srcObject = stream;
        await v.play();
        while (!stop) {
          grab.width = v.videoWidth;
          grab.height = v.videoHeight;
          grab.getContext("2d")!.drawImage(v, 0, 0);
          const frame = await new Promise<Blob | null>((r) => grab.toBlob(r, "image/jpeg", 0.7));
          const res = await fetch("/api/detect", { method: "POST", body: frame });
          if (!res.ok) throw new Error(`Detection failed (${res.status})`);
          const data = await res.json();
          if (stop) break;
          draw(data.detections);
          if (data.announce) say(data.description);
          await new Promise((r) => setTimeout(r, 250));
        }
      } catch (e) {
        if (stop) return;
        setError(e instanceof Error ? e.message : String(e));
        setRunning(false);
      }
    })();

    return () => {
      stop = true;
      stream?.getTracks().forEach((t) => t.stop());
      speechSynthesis.cancel();
    };
  }, [running]);

  async function ask(text: string) {
    if (!text.trim()) return;
    setQuestion("");
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text.trim().slice(0, 200) }),
      });
      if (!res.ok) throw new Error(`Question failed (${res.status})`);
      say((await res.json()).answer);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  function listen() {
    speechSynthesis.cancel(); // otherwise the microphone hears our own narration
    // Short tone so a user who cannot see the screen knows listening has started.
    const audio = new AudioContext();
    const tone = audio.createOscillator();
    tone.connect(audio.destination);
    tone.start();
    tone.stop(audio.currentTime + 0.15);
    const recognition = new Recognition();
    recognition.onresult = (event: any) => ask(event.results[0][0].transcript);
    recognition.onerror = (event: any) => setError(`Could not hear a question (${event.error}).`);
    recognition.start();
  }

  return (
    <main>
      <h1>Pathfinder</h1>
      <p className="note">
        Experimental awareness aid. It is not a navigation or collision-avoidance system and
        does not replace a white cane, guide dog, or mobility training. Detection can be wrong.
      </p>

      <div className="controls">
        <button
          className="primary"
          onClick={() => {
            setError("");
            setRunning(!running);
          }}
        >
          {running ? "Stop camera" : "Start camera"}
        </button>
        <button
          aria-pressed={isMuted}
          onClick={() => {
            muted.current = !isMuted;
            setIsMuted(!isMuted);
            speechSynthesis.cancel();
          }}
        >
          {isMuted ? "Unmute voice" : "Mute voice"}
        </button>
      </div>

      {Recognition && (
        <button className="voice primary" onClick={listen}>
          Ask by voice
        </button>
      )}

      <p className="spoken" aria-live="polite">{spoken}</p>
      {error && <p className="error" role="alert">{error}</p>}

      <form
        onSubmit={(event: FormEvent) => {
          event.preventDefault();
          ask(question);
        }}
      >
        <input
          aria-label="Ask about the scene"
          placeholder="Where is the chair?"
          maxLength={200}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button type="submit">Ask</button>
        <button type="button" onClick={() => ask("Read the text")}>
          Read text
        </button>
      </form>

      <div className="view">
        <video ref={video} muted playsInline aria-label="Camera preview" />
        <canvas ref={overlay} aria-hidden="true" />
      </div>

      <h2>Recent announcements</h2>
      <ol>
        {history.map((entry) => (
          <li key={entry.id}>
            <time>{new Date(entry.created_at.replace(" ", "T") + "Z").toLocaleTimeString()}</time>
            {entry.text}
          </li>
        ))}
      </ol>
    </main>
  );
}
