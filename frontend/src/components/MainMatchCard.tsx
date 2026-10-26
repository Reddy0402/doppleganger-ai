import React, { useState } from "react";
import { Sparkles, Info, Share2, Split, Trash2, RotateCcw, Compass } from "lucide-react";
import type { MatchCandidate, QualityAssessment, SearchStats } from "../types";
import { resolveImageUrl } from "../services/api";

interface MainMatchCardProps {
  topMatch: MatchCandidate;
  userImageSrc?: string;
  quality?: QualityAssessment;
  stats?: SearchStats;
  modelName: string;
  dimension: number;
  latencyMs: number;
  onOpenSideBySide: (candidate: MatchCandidate) => void;
  onOpenShareCard: (candidate: MatchCandidate) => void;
  onPurgeData: () => void;
  onRetry: () => void;
}

export const MainMatchCard: React.FC<MainMatchCardProps> = ({
  topMatch,
  userImageSrc,
  quality,
  stats,
  modelName,
  dimension,
  latencyMs,
  onOpenSideBySide,
  onOpenShareCard,
  onPurgeData,
  onRetry,
}) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const getBadgeClass = (tier: string) => {
    switch (tier) {
      case "Remarkable Doppelgänger":
        return "bg-violet-600/30 text-violet-300 border-violet-500/50 shadow-glow";
      case "Strong Resemblance":
        return "bg-cyan-500/30 text-cyan-300 border-cyan-500/50 shadow-glow-cyan";
      default:
        return "bg-slate-800 text-slate-300 border-white/10";
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Search Summary Dashboard Banner */}
      {stats && (
        <div className="mb-6 p-5 rounded-2xl glass-panel border border-cyan-500/20 shadow-xl bg-gradient-to-r from-midnight-900/90 via-midnight-900/60 to-midnight-900/90">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/5">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 font-mono">
                Full-Gallery Discovery Summary
              </span>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>Searched {stats.total_participants_searched} Authorized Participants</span>
                <span className="text-xs font-normal text-slate-400">({stats.total_portraits_indexed} reference portraits)</span>
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-bold font-mono">
                {stats.total_qualifying} Qualifying Lookalikes
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-center">
            <div className="p-2 rounded-xl bg-white/[0.02] border border-white/5">
              <div className="text-xs text-slate-400">Threshold</div>
              <div className="text-sm font-bold font-mono text-cyan-300">≥ {stats.resemblance_threshold}%</div>
            </div>
            <div className="p-2 rounded-xl bg-white/[0.02] border border-white/5">
              <div className="text-xs text-slate-400">Search Time</div>
              <div className="text-sm font-bold font-mono text-violet-300">{stats.search_duration_ms} ms</div>
            </div>
            <div className="p-2 rounded-xl bg-white/[0.02] border border-white/5">
              <div className="text-xs text-slate-400">Recognition Model</div>
              <div className="text-xs font-bold font-mono text-slate-200 truncate">{stats.recognition_model}</div>
            </div>
            <div className="p-2 rounded-xl bg-white/[0.02] border border-white/5">
              <div className="text-xs text-slate-400">Face Detector</div>
              <div className="text-xs font-bold font-mono text-slate-200 truncate">{stats.detector}</div>
            </div>
          </div>

          {/* Tier Counts Pill Bar */}
          <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-white/5 text-[11px]">
            <span className="text-slate-400 font-medium">Cohort Breakdown:</span>
            <span className="px-2 py-0.5 rounded bg-violet-500/20 text-violet-300 font-semibold">
              Remarkable: {stats.tier_counts.exceptional}
            </span>
            <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-semibold">
              Strong: {stats.tier_counts.strong}
            </span>
            <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-semibold">
              Moderate: {stats.tier_counts.moderate}
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold">
              Subtle: {stats.tier_counts.subtle}
            </span>
          </div>
        </div>
      )}

      {/* Quality Warnings Banner if any */}
      {quality && quality.warnings.length > 0 && (
        <div className="mb-6 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-3">
          <Info className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
          <div>
            <span className="font-semibold block mb-0.5">Image Quality Notice</span>
            <ul className="list-disc pl-4 space-y-0.5 text-amber-300/90">
              {quality.warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Main Glassmorphic Card */}
      <div className="glass-panel rounded-3xl border border-white/10 p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500" />

        {/* Top Header Row */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-6 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-violet-600/30 text-violet-300 border border-violet-500/30">
                #1 Visual Match
              </span>
              <span className="text-xs text-slate-400 font-mono">
                {modelName.toUpperCase()} ({dimension}D) &bull; {latencyMs}ms
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
              {topMatch.display_name}
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
              {topMatch.bio_caption || "Authorized Portrait Participant"}
            </p>
          </div>

          {/* Resemblance Score Pill */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <div
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
                className={`px-4 py-2 rounded-2xl border text-center cursor-help transition-all ${getBadgeClass(topMatch.resemblance_tier)}`}
              >
                <div className="text-2xl sm:text-3xl font-extrabold font-display leading-none">
                  {topMatch.resemblance_percentage}%
                </div>
                <div className="text-[10px] font-semibold uppercase tracking-wider mt-1 opacity-90 flex items-center justify-center gap-1">
                  <span>{topMatch.resemblance_tier}</span>
                  <Info className="w-3 h-3" />
                </div>
              </div>

              {/* Explanatory Tooltip */}
              {showTooltip && (
                <div className="absolute right-0 top-full mt-2 w-72 p-3.5 rounded-xl bg-midnight-900 border border-white/20 text-[11px] text-slate-300 shadow-2xl z-30 leading-snug">
                  <p className="font-semibold text-white mb-1">How Resemblance is Calculated:</p>
                  <p className="mb-2">
                    Raw ArcFace cosine similarity ({topMatch.similarity_score}) mapped to a calibrated human lookalike scale. High scores represent geometric alignment of bone contours, eye distance, and nasal angles.
                  </p>
                  <p className="text-[10px] text-slate-400 border-t border-white/10 pt-1.5">
                    *Does not represent genetic relation or biological identity.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Side-by-Side Dual Portrait View */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
          {/* User Selfie */}
          <div className="relative rounded-2xl overflow-hidden bg-midnight-950 border border-white/10 group aspect-square flex items-center justify-center">
            {userImageSrc ? (
              <img
                src={userImageSrc}
                alt="Your Uploaded Portrait"
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="text-center p-4 text-slate-500">
                <p className="text-xs">Your Query Portrait</p>
              </div>
            )}
            <div className="absolute bottom-3 left-3 bg-midnight-950/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-xs font-semibold text-white border border-white/10 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              <span>Your Portrait</span>
            </div>
          </div>

          {/* Doppelgänger Match */}
          <div className="relative rounded-2xl overflow-hidden bg-midnight-950 border border-violet-500/40 group aspect-square shadow-glow">
            <img
              src={resolveImageUrl(topMatch.image_url)}
              alt={topMatch.display_name}
              className="w-full h-full object-cover"
            />
            <div className="absolute bottom-3 left-3 bg-midnight-950/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-xs font-semibold text-violet-300 border border-violet-500/30 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-violet-400" />
              <span>Matched Doppelgänger</span>
            </div>

            <div className="absolute top-3 right-3 bg-midnight-950/80 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-mono text-slate-300 border border-white/10">
              {topMatch.license_info}
            </div>
          </div>
        </div>

        {/* Fun Algorithmic Match Caption */}
        {topMatch.fun_caption && (
          <div className="mb-6 p-4 rounded-2xl bg-gradient-to-r from-violet-600/15 via-indigo-600/10 to-cyan-500/15 border border-violet-500/30 text-center">
            <p className="text-xs sm:text-sm text-slate-200 italic font-medium">
              "{topMatch.fun_caption}"
            </p>
          </div>
        )}

        {/* Detailed Subfeature Geometric Breakdown */}
        {topMatch.subfeature_breakdown && (
          <div className="mb-8 p-5 rounded-2xl bg-midnight-900/80 border border-white/5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
              <Compass className="w-4 h-4 text-cyan-400" />
              <span>Facial Anatomy Alignment Breakdown</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {Object.entries(topMatch.subfeature_breakdown).map(([region, data]) => (
                <div key={region} className="p-3 rounded-xl bg-midnight-950 border border-white/5">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-medium text-slate-300">{data.label}</span>
                    <span className="text-xs font-bold text-cyan-400">{data.score}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-violet-500 to-cyan-400 rounded-full transition-all duration-500"
                      style={{ width: `${data.score}%` }}
                    />
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1 font-mono">
                    Cosine: {data.raw_cosine}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Primary Action Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-white/10">
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => onOpenSideBySide(topMatch)}
              className="px-4 py-2.5 rounded-xl glass-panel text-slate-200 hover:text-white hover:bg-white/10 text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer"
            >
              <Split className="w-4 h-4 text-cyan-400" />
              <span>Compare Fullscreen</span>
            </button>

            <button
              onClick={() => onOpenShareCard(topMatch)}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white text-xs font-semibold flex items-center gap-2 shadow-glow transition-all cursor-pointer"
            >
              <Share2 className="w-4 h-4" />
              <span>Save & Download Card</span>
            </button>

            <button
              onClick={onRetry}
              className="px-4 py-2.5 rounded-xl glass-panel text-slate-300 hover:text-white text-xs font-medium flex items-center gap-2 transition-all cursor-pointer"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Try Another Photo</span>
            </button>
          </div>

          {/* Ephemeral Privacy Purge Button */}
          <button
            onClick={onPurgeData}
            className="px-3.5 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
            title="Immediately purge all temporary session data"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Purge Session Data</span>
          </button>
        </div>
      </div>
    </div>
  );
};
