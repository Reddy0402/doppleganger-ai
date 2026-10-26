import React from "react";
import { ArrowRight, Sparkles, ShieldCheck, Cpu, Eye, Lock } from "lucide-react";

interface LandingHeroProps {
  onStart: () => void;
  onExploreGallery: () => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onStart, onExploreGallery }) => {
  return (
    <div className="relative pt-8 pb-16 overflow-hidden">
      {/* Background ambient orbs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-violet-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 left-1/3 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center relative z-10">
        {/* Pill Tag */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-medium mb-6 animate-pulse-slow">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Computer Vision & Deep Resemblance Retrieval</span>
        </div>

        {/* Editorial Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white mb-6 leading-[1.1]">
          Somewhere in the world, <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-violet-400 via-indigo-300 to-cyan-400">
            there's a face that looks like yours.
          </span>
        </h1>

        <p className="max-w-2xl mx-auto text-slate-300 text-base sm:text-lg mb-8 font-light leading-relaxed">
          Upload a portrait to analyze facial symmetry, orbital spacing, and jawline contours using 
          state-of-the-art ArcFace embeddings. Discover your visual lookalikes across our authorized gallery.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
          <button
            onClick={onStart}
            id="btn-find-doppelganger-hero"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 text-white font-semibold text-sm shadow-glow hover:shadow-cyan-500/30 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 flex items-center justify-center gap-2 group cursor-pointer"
          >
            <span>Find My Doppelgänger</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>

          <button
            onClick={onExploreGallery}
            className="w-full sm:w-auto px-6 py-3.5 rounded-xl glass-panel text-slate-200 hover:text-white hover:bg-white/10 text-sm font-medium transition-all duration-200 cursor-pointer"
          >
            Explore Authorized Gallery
          </button>
        </div>

        {/* Trust & Pipeline Architecture Badges */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-3xl mx-auto text-left">
          <div className="glass-panel p-3.5 rounded-xl border border-white/5">
            <div className="flex items-center gap-2 mb-1">
              <Eye className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-semibold text-white">5-Point Alignment</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-snug">
              OpenCV YuNet canonical landmark normalization.
            </p>
          </div>

          <div className="glass-panel p-3.5 rounded-xl border border-white/5">
            <div className="flex items-center gap-2 mb-1">
              <Cpu className="w-4 h-4 text-violet-400" />
              <span className="text-xs font-semibold text-white">ArcFace Neural Model</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-snug">
              128D unit-normalized high-dimensional feature space.
            </p>
          </div>

          <div className="glass-panel p-3.5 rounded-xl border border-white/5">
            <div className="flex items-center gap-2 mb-1">
              <Lock className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-semibold text-white">Zero Persistent Storage</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-snug">
              Uploads purged immediately from memory after search.
            </p>
          </div>

          <div className="glass-panel p-3.5 rounded-xl border border-white/5">
            <div className="flex items-center gap-2 mb-1">
              <ShieldCheck className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-semibold text-white">Ethical Transparency</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-snug">
              Strictly perceptual resemblance; no genetic claims.
            </p>
          </div>
        </div>

        {/* Interactive Demo Preview Cards */}
        <div className="mt-14 max-w-4xl mx-auto glass-panel p-6 rounded-2xl border border-white/10 text-left">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Preview Authorized Portrait Matches</h3>
              <p className="text-xs text-slate-400">Consented synthetic portrait cohort with calibrated similarity metrics</p>
            </div>
            <span className="text-xs text-violet-400 font-mono">Top-Match Previews</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { name: "Elena Vance", match: "91.4%", tier: "Remarkable", file: "portrait_elena_1.jpg", sub: "Architectural Designer" },
              { name: "Marcus Thorne", match: "88.6%", tier: "Strong", file: "portrait_marcus_1.jpg", sub: "Sound Producer" },
              { name: "Aisha Patel", match: "84.2%", tier: "Strong", file: "portrait_aisha_1.jpg", sub: "Research Scientist" },
              { name: "Kai Tanaka", match: "82.5%", tier: "Noticeable", file: "portrait_kai_1.jpg", sub: "Industrial Designer" }
            ].map((p, idx) => (
              <div key={idx} className="glass-panel rounded-xl overflow-hidden group hover:border-violet-500/40 transition-all">
                <div className="relative aspect-square overflow-hidden bg-slate-900">
                  <img
                    src={`/api/gallery/images/${p.file}`}
                    alt={p.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-2 right-2 bg-midnight-950/80 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-bold text-cyan-300 border border-cyan-500/30">
                    {p.match}
                  </div>
                </div>
                <div className="p-2.5">
                  <h4 className="text-xs font-semibold text-white truncate">{p.name}</h4>
                  <p className="text-[10px] text-slate-400 truncate">{p.sub}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
