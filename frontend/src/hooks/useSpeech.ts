import { useCallback, useRef, useState } from "react";
const Recognition = (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition;
export function useSpeech() {
  const mutedRef = useRef(false);
  const [muted, setMuted] = useState(false);
  const supported = Boolean(Recognition);
  const speak = useCallback((message: string) => {
    if (!message || mutedRef.current || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(message));
  }, []);
  const stopSpeaking = useCallback(() => { if ("speechSynthesis" in window) window.speechSynthesis.cancel(); }, []);
  const toggleMute = useCallback(() => { mutedRef.current = !mutedRef.current; setMuted(mutedRef.current); stopSpeaking(); }, [stopSpeaking]);
  const listen = useCallback((onText: (text: string) => void, onError: (message: string) => void) => {
    if (!Recognition) { onError("Voice questions are not supported in this browser. Try Chrome or Safari."); return; }
    stopSpeaking();
    const recognition = new Recognition();
    recognition.lang = "en-US"; recognition.interimResults = false; recognition.maxAlternatives = 1;
    recognition.onresult = (event: any) => onText(event.results[0][0].transcript);
    recognition.onerror = (event: any) => onError("I couldn't hear that clearly (" + event.error + ").");
    recognition.start();
  }, [stopSpeaking]);
  return { muted, supported, speak, stopSpeaking, toggleMute, listen };
}