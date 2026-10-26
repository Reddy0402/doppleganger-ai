import React, { useEffect, useState } from "react";
import { CheckCircle2, Loader2, Sparkles, Scan, ShieldCheck, Cpu, Database } from "lucide-react";

interface AnalysisProgressProps {
  isLoading: boolean;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ isLoading }) => {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      setActiveStep(0);
      return;
    }

    // Progress through verified steps
    const t1 = setTimeout(() => setActiveStep(1), 150);
    const t2 = setTimeout(() => setActiveStep(2), 350);
    const t3 = setTimeout(() => setActiveStep(3), 600);
    const t4 = setTimeout(() => setActiveStep(4), 900);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
    };
  }, [isLoading]);

  if (!isLoading) return null;

  const steps = [
    { title: "File Security & Decompression", desc: "Validating magic bytes, EXIF orientation, and format constraints", icon: ShieldCheck },
    { title: "Face Landmark Alignment", desc: "Detecting 5 canonical points (eyes, nose, mouth) with OpenCV YuNet", icon: Scan },
    { title: "Quality & Blur Assessment", desc: "Evaluating Laplacian variance sharpness and luminance exposure", icon: Sparkles },
    { title: "ArcFace Embedding Generation", desc: "Extracting 128D unit-normalized feature vector", icon: Cpu },
    { title: "Gallery Vector Retrieval", desc: "Executing exact cosine similarity search across authorized cohort", icon: Database },
  ];

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-violet-500/30 shadow-glow relative overflow-hidden">
        {/* Animated scanning line */}
        <div className="biometric-scanner-line opacity-50" />

        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/20 text-violet-300 text-xs font-semibold mb-2">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
            <span>Real-Time Inference Active</span>
          </div>
          <h3 className="text-xl font-bold text-white">
            Analyzing Facial Geometry
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Running deep landmark alignment and high-dimensional embedding matching
          </p>
        </div>

        <div className="space-y-3.5">
          {steps.map((st, idx) => {
            const Icon = st.icon;
            const isDone = activeStep > idx;
            const isCurrent = activeStep === idx;

            return (
              <div
                key={idx}
                className={`p-3.5 rounded-xl border transition-all duration-300 flex items-start gap-3.5 ${
                  isCurrent
                    ? "bg-violet-600/15 border-violet-500/50 shadow-glow"
                    : isDone
                    ? "bg-midnight-900/80 border-emerald-500/30"
                    : "bg-midnight-900/30 border-white/5 opacity-50"
                }`}
              >
                <div className="mt-0.5">
                  {isDone ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-5 h-5 animate-spin text-cyan-400 shrink-0" />
                  ) : (
                    <Icon className="w-5 h-5 text-slate-500 shrink-0" />
                  )}
                </div>
                <div>
                  <h4 className={`text-xs font-semibold ${isCurrent ? "text-cyan-300" : isDone ? "text-white" : "text-slate-400"}`}>
                    {st.title}
                  </h4>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                    {st.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
