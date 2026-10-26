import React, { useState } from "react";
import { X, Shield, Sliders } from "lucide-react";
import type { MatchCandidate } from "../types";
import { resolveImageUrl } from "../services/api";

interface SideBySideModalProps {
  candidate: MatchCandidate | null;
  userImageSrc?: string;
  onClose: () => void;
}

export const SideBySideModal: React.FC<SideBySideModalProps> = ({
  candidate,
  userImageSrc,
  onClose,
}) => {
  const [showGuides, setShowGuides] = useState(true);

  if (!candidate) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="glass-panel w-full max-w-4xl rounded-3xl border border-white/20 p-6 sm:p-8 shadow-2xl relative max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full glass-panel text-slate-300 hover:text-white transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-cyan-400">Rank #{candidate.rank}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-violet-600/30 text-violet-300 font-bold">
                {candidate.resemblance_percentage}% Resemblance
              </span>
            </div>
            <h3 className="text-xl font-bold text-white mt-1">
              Side-by-Side Face Geometry Analysis
            </h3>
          </div>

          <button
            onClick={() => setShowGuides(!showGuides)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer ${
              showGuides
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "glass-panel text-slate-400 hover:text-white"
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>{showGuides ? "Hide Alignment Guides" : "Show Alignment Guides"}</span>
          </button>
        </div>

        {/* Dual Portraits with Alignment Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* User Face */}
          <div className="relative aspect-square rounded-2xl overflow-hidden bg-midnight-950 border border-white/10">
            {userImageSrc ? (
              <img src={userImageSrc} alt="Your Face" className="w-full h-full object-cover" />
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500">Your Portrait</div>
            )}
            
            {showGuides && (
              <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-8 border border-cyan-400/20">
                <div className="w-full h-[1px] bg-cyan-400/40 top-[35%] relative" title="Eye Orbital Line" />
                <div className="w-full h-[1px] bg-cyan-400/40 top-[55%] relative" title="Nasal Base Line" />
                <div className="w-full h-[1px] bg-cyan-400/40 top-[75%] relative" title="Lip Contour Line" />
                <div className="h-full w-[1px] bg-cyan-400/40 left-[50%] absolute top-0" title="Facial Symmetry Axis" />
              </div>
            )}
            <div className="absolute bottom-3 left-3 bg-midnight-950/90 px-3 py-1 rounded-lg text-xs font-bold text-white border border-white/10">
              Your Portrait
            </div>
          </div>

          {/* Candidate Face */}
          <div className="relative aspect-square rounded-2xl overflow-hidden bg-midnight-950 border border-violet-500/40 shadow-glow">
            <img src={resolveImageUrl(candidate.image_url)} alt={candidate.display_name} className="w-full h-full object-cover" />
            
            {showGuides && (
              <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-8 border border-violet-400/20">
                <div className="w-full h-[1px] bg-violet-400/40 top-[35%] relative" />
                <div className="w-full h-[1px] bg-violet-400/40 top-[55%] relative" />
                <div className="w-full h-[1px] bg-violet-400/40 top-[75%] relative" />
                <div className="h-full w-[1px] bg-violet-400/40 left-[50%] absolute top-0" />
              </div>
            )}
            <div className="absolute bottom-3 left-3 bg-midnight-950/90 px-3 py-1 rounded-lg text-xs font-bold text-violet-300 border border-violet-500/30">
              {candidate.display_name} (Candidate)
            </div>
          </div>
        </div>

        {/* Feature Alignment Table */}
        {candidate.subfeature_breakdown && (
          <div className="p-4 rounded-xl bg-midnight-900 border border-white/10 mb-6">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
              Geometric Correspondence by Anatomical Region
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {Object.entries(candidate.subfeature_breakdown).map(([k, v]) => (
                <div key={k} className="p-2.5 rounded-lg bg-midnight-950 border border-white/5">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">{v.label}</span>
                    <span className="font-bold text-cyan-400">{v.score}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-400 rounded-full" style={{ width: `${v.score}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="text-center text-xs text-slate-400 flex items-center justify-center gap-1.5">
          <Shield className="w-3.5 h-3.5 text-emerald-400" />
          <span>Biometric Disclaimer: Geometric similarity does not indicate genetic or biological kinship.</span>
        </div>
      </div>
    </div>
  );
};
