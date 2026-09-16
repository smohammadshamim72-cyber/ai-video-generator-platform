import { useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  Film,
  LoaderCircle,
  Play,
  Sparkles,
  Wand2,
} from "lucide-react";

const steps = [
  "Scripting",
  "Storyboarding",
  "Scene 1 Generating",
  "Scene 2 Generating",
  "Scene 3 Generating",
  "Final Rendering",
];

const durationOptions = Array.from({ length: 24 }, (_, index) => index + 1);

export default function VideoGeneratorDashboard() {
  const [prompt, setPrompt] = useState(
    "A cinematic futuristic city at sunrise, with autonomous vehicles flying through glowing streets while a lonely hero discovers a hidden memory archive in the clouds."
  );
  const [duration, setDuration] = useState(4);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [videoReady, setVideoReady] = useState(false);
  const [progressMessage, setProgressMessage] = useState("Ready to generate");

  const handleGenerate = () => {
    setIsGenerating(true);
    setVideoReady(false);
    setCurrentStep(0);
    setProgressMessage("Agent is scripting your narrative...");

    let stepIndex = 0;
    const interval = setInterval(() => {
      stepIndex += 1;
      setCurrentStep((prev) => Math.min(stepIndex, steps.length - 1));

      if (stepIndex === 1) {
        setProgressMessage("Narrative structure generated.");
      } else if (stepIndex === 2) {
        setProgressMessage("Storyboarding key scenes and visual prompts.");
      } else if (stepIndex >= 3 && stepIndex < steps.length - 1) {
        setProgressMessage(`Scene ${stepIndex - 2} generating with continuation context...`);
      } else if (stepIndex === steps.length - 1) {
        setProgressMessage("Final rendering and audio sync in progress...");
      }

      if (stepIndex >= steps.length) {
        clearInterval(interval);
        setIsGenerating(false);
        setVideoReady(true);
        setProgressMessage("Final video ready.");
      }
    }, 1100);
  };

  const renderStepState = (index: number) => {
    if (isGenerating && index <= currentStep) {
      return "active";
    }

    if (videoReady && index === steps.length - 1) {
      return "done";
    }

    if (index < currentStep) {
      return "done";
    }

    return "pending";
  };

  return (
    <main className="min-h-screen px-4 py-8 text-slate-100 md:px-10">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="mb-2 inline-flex items-center gap-2 rounded-full border border-cyan-500/40 bg-cyan-500/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-cyan-300">
              <Sparkles className="h-3.5 w-3.5" />
              AI Video Studio
            </p>
            <h1 className="text-3xl font-bold tracking-tight md:text-4xl">Long-form Video Generator</h1>
          </div>

          <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-slate-900/60 px-3 py-2 text-sm text-slate-300 shadow-xl backdrop-blur">
            <Clock3 className="h-4 w-4 text-cyan-300" />
            {duration} min project
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.35fr_0.9fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-2xl backdrop-blur-xl">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-xl bg-cyan-500/15 p-2 text-cyan-300">
                <Wand2 className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Create a new generation</h2>
                <p className="text-sm text-slate-400">Prompt, style, and duration</p>
              </div>
            </div>

            <div className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">Prompt</label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={7}
                  className="w-full resize-none rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-3 text-base text-slate-100 outline-none ring-0 transition focus:border-cyan-400"
                  placeholder="Describe the story, setting, mood, and camera movement..."
                />
              </div>

              <div className="grid gap-5 md:grid-cols-[220px_1fr]">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-300">Video length</label>
                  <select
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    className="w-full rounded-2xl border border-white/10 bg-slate-900/80 px-3 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  >
                    {durationOptions.map((option) => (
                      <option key={option} value={option}>
                        {option} min
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-end">
                  <button
                    type="button"
                    onClick={handleGenerate}
                    disabled={isGenerating}
                    className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-cyan-500 px-5 py-3.5 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {isGenerating ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
                    {isGenerating ? "Generating..." : "Generate Video"}
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-8 rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-4">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Live status</p>
                  <p className="mt-1 text-base font-medium text-slate-100">{progressMessage}</p>
                </div>
                {isGenerating ? (
                  <div className="rounded-full bg-slate-900 px-3 py-1.5 text-xs text-cyan-300">
                    Processing
                  </div>
                ) : (
                  <div className="rounded-full bg-emerald-500/15 px-3 py-1.5 text-xs text-emerald-300">
                    Idle
                  </div>
                )}
              </div>
            </div>
          </section>

          <aside className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-2xl backdrop-blur-xl">
            <div className="mb-4 flex items-center gap-3">
              <div className="rounded-xl bg-violet-500/15 p-2 text-violet-300">
                <Film className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Video Preview</h3>
                <p className="text-sm text-slate-400">Final MP4 output</p>
              </div>
            </div>

            <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900">
              {videoReady ? (
                <video
                  className="h-[280px] w-full object-cover"
                  controls
                  poster="https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=1200&q=80"
                >
                  <source src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4" type="video/mp4" />
                </video>
              ) : (
                <div className="flex h-[280px] flex-col items-center justify-center gap-3 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950 text-slate-400">
                  <Play className="h-10 w-10 text-cyan-300" />
                  <p className="text-center text-sm">Your final video preview will appear here once generation completes.</p>
                </div>
              )}
            </div>
          </aside>
        </div>

        <section className="mt-8 rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-2xl backdrop-blur-xl">
          <div className="mb-4 flex items-center gap-3">
            <div className="rounded-xl bg-amber-500/15 p-2 text-amber-300">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-xl font-semibold">Generation Timeline</h3>
              <p className="text-sm text-slate-400">Agentic AI process and autoregressive continuation</p>
            </div>
          </div>

          <div className="space-y-4">
            {steps.map((step, index) => {
              const state = renderStepState(index);

              return (
                <div key={step} className="flex items-start gap-4">
                  <div className="relative flex flex-col items-center">
                    <div
                      className={`flex h-9 w-9 items-center justify-center rounded-full border text-sm font-medium ${
                        state === "done"
                          ? "border-emerald-400 bg-emerald-500/15 text-emerald-300"
                          : state === "active"
                            ? "border-cyan-400 bg-cyan-500/15 text-cyan-300"
                            : "border-slate-600 bg-slate-800 text-slate-400"
                      }`}
                    >
                      {state === "done" ? <CheckCircle2 className="h-4 w-4" /> : index + 1}
                    </div>
                    {index !== steps.length - 1 && <div className="mt-2 h-10 w-px bg-slate-700" />}
                  </div>

                  <div
                    className={`flex-1 rounded-2xl border px-4 py-3 ${
                      state === "done"
                        ? "border-emerald-500/30 bg-emerald-500/5"
                        : state === "active"
                          ? "border-cyan-500/30 bg-cyan-500/5"
                          : "border-white/10 bg-slate-900/60"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-medium text-slate-100">{step}</p>
                      {state === "active" && <LoaderCircle className="h-4 w-4 animate-spin text-cyan-300" />}
                    </div>
                    <p className="mt-1 text-sm text-slate-400">
                      {state === "done"
                        ? "Completed successfully."
                        : state === "active"
                          ? "Running now..."
                          : "Waiting for the next stage."}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </main>
  );
}
