import { useCallback, useEffect, useRef, useState } from "react";

export type GenerationEvent = {
  type: "snapshot" | "progress" | "done" | "error" | "heartbeat";
  message?: string;
  output_url?: string;
  stage?: string;
  scene?: number;
  total?: number;
};

const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
const WS_URL = API_URL.replace(/^http/, "ws");

export function useVideoGeneration() {
  const socketRef = useRef<WebSocket | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [events, setEvents] = useState<GenerationEvent[]>([]);
  const [outputUrl, setOutputUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startGeneration = useCallback(async (prompt: string, duration: number) => {
    setIsGenerating(true); setEvents([]); setOutputUrl(null); setError(null);
    try {
      const response = await fetch(`${API_URL}/api/generate-video`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, target_duration_minutes: duration, style: "cinematic" }),
      });
      if (!response.ok) throw new Error("Unable to create generation job");
      const { job_id } = await response.json();
      const socket = new WebSocket(`${WS_URL}/ws/jobs/${job_id}`);
      socketRef.current = socket;
      socket.onmessage = (message) => {
        const event = JSON.parse(message.data) as GenerationEvent;
        setEvents((previous) => [...previous, event]);
        if (event.type === "done") { setOutputUrl(event.output_url || null); setIsGenerating(false); socket.close(); }
        if (event.type === "error") { setError(event.message || "Generation failed"); setIsGenerating(false); }
      };
      socket.onerror = () => { setError("Realtime connection failed"); setIsGenerating(false); };
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Generation failed");
      setIsGenerating(false);
    }
  }, []);

  useEffect(() => () => socketRef.current?.close(), []);
  return { isGenerating, events, outputUrl, error, startGeneration };
}
