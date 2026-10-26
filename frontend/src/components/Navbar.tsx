import React from "react";
import { Sparkles, Shield, Database, BarChart3, ScanFace } from "lucide-react";

interface NavbarProps {
  activeTab: "match" | "gallery" | "evaluation" | "privacy";
  setActiveTab: (tab: "match" | "gallery" | "evaluation" | "privacy") => void;
  activeModel: string;
  onSelectModel: (model: string) => void;
  galleryCount: number;
  apiOnline: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  activeModel,
  onSelectModel,
  galleryCount,
  apiOnline,
}) => {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/10 px-4 lg:px-8 py-3.5 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => setActiveTab("match")}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="relative w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 via-indigo-600 to-cyan-500 p-0.5 shadow-glow group-hover:scale-105 transition-transform duration-300">
            <div className="w-full h-full bg-midnight-950 rounded-[10px] flex items-center justify-center">
              <ScanFace className="w-5 h-5 text-cyan-400 group-hover:text-white transition-colors" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display font-bold text-lg text-white tracking-tight">
                Doppelgänger
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-violet-500/20 text-violet-400 border border-violet-500/30 rounded">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">
              Perceptual Face Resemblance Engine
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-2">
          <button
            onClick={() => setActiveTab("match")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === "match"
                ? "bg-violet-600 text-white shadow-glow"
                : "text-slate-300 hover:text-white hover:bg-white/5"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Discover</span>
          </button>

          <button
            onClick={() => setActiveTab("gallery")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === "gallery"
                ? "bg-violet-600 text-white shadow-glow"
                : "text-slate-300 hover:text-white hover:bg-white/5"
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Authorized</span> Gallery
            {galleryCount > 0 && (
              <span className="ml-1 px-1.5 py-0.2 text-[10px] bg-slate-800 text-slate-300 rounded-full">
                {galleryCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("evaluation")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === "evaluation"
                ? "bg-violet-600 text-white shadow-glow"
                : "text-slate-300 hover:text-white hover:bg-white/5"
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Benchmarks &</span> Metrics
          </button>

          <button
            onClick={() => setActiveTab("privacy")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === "privacy"
                ? "bg-violet-600 text-white shadow-glow"
                : "text-slate-300 hover:text-white hover:bg-white/5"
            }`}
          >
            <Shield className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Privacy</span>
          </button>
        </nav>

        {/* Model Switcher & Status */}
        <div className="hidden lg:flex items-center gap-3">
          <div className="flex items-center gap-2 bg-midnight-900 border border-white/10 rounded-lg px-2.5 py-1 text-xs">
            <span className="text-slate-400">Model:</span>
            <select
              value={activeModel}
              onChange={(e) => onSelectModel(e.target.value)}
              className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
            >
              <option value="sface" className="bg-midnight-900 text-slate-100">
                SFace (OpenCV 128D)
              </option>
              <option value="deterministic" className="bg-midnight-900 text-slate-100">
                Spatial Baseline (128D)
              </option>
            </select>
          </div>

          <div className="flex items-center gap-2 pl-2 border-l border-white/10">
            <span className={`w-2 h-2 rounded-full ${apiOnline ? "bg-emerald-400 animate-pulse" : "bg-rose-500"}`} />
            <span className="text-[11px] text-slate-400 font-mono">
              {apiOnline ? "API Online" : "Connecting..."}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
