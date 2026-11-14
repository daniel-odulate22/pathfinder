import type { Announcement, DetectionResponse, QuestionResponse } from "../types";
async function checked<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error("Pathfinder request failed (" + response.status + ").");
  return response.json() as Promise<T>;
}
export async function detectFrame(frame: Blob, signal?: AbortSignal) {
  return checked<DetectionResponse>(await fetch("/api/detect", { method: "POST", body: frame, signal }));
}
export async function askPathfinder(question: string) {
  return checked<QuestionResponse>(await fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: question.trim().slice(0, 200) }) }));
}
export async function getHistory() { return checked<Announcement[]>(await fetch("/api/history")); }