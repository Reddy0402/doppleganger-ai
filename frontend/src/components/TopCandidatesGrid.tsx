import React, { useState } from "react";
import { Split, Share2, Filter, ArrowUpDown } from "lucide-react";
import type { MatchCandidate } from "../types";
import { resolveImageUrl } from "../services/api";

interface TopCandidatesGridProps {
  candidates: MatchCandidate[];
  totalQualifying?: number;
  onOpenSideBySide: (candidate: MatchCandidate) => void;
  onOpenShareCard: (candidate: MatchCandidate) => void;
}

export const TopCandidatesGrid: React.FC<TopCandidatesGridProps> = ({
  candidates,
  totalQualifying,
  onOpenSideBySide,
  onOpenShareCard,
}) => {
  const [tierFilter, setTierFilter] = useState<string>("all");
  const [sortOrder, setSortOrder] = useState<"desc" | "asc">("desc");
  const [displayCount, setDisplayCount] = useState<number>(6);

  if (!candidates || candidates.length <= 1) return null;

  // Filter out the primary #1 candidate which is displayed prominently in MainMatchCard
  const remaining = candidates.slice(1);

  // Filter by resemblance tier
  const filtered = remaining.filter((c) => {
    if (tierFilter === "all") return true;
    if (tierFilter === "remarkable") return c.resemblance_percentage >= 82;
    if (tierFilter === "strong") return c.resemblance_percentage >= 65 && c.resemblance_percentage < 82;
    if (tierFilter === "moderate") return c.resemblance_percentage >= 45 && c.resemblance_percentage < 65;
    if (tierFilter === "subtle") return c.resemblance_percentage < 45;
    return true;
  });

  // Sort by score
  const sorted = [...filtered].sort((a, b) => {
    return sortOrder === "desc"
      ? b.similarity_score - a.similarity_score
      : a.similarity_score - b.similarity_score;
  });

  const displayed = sorted.slice(0, displayCount);

  return (
    <div className="max-w-4xl mx-auto px-4 pb-12">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <span>Ranked Gallery Lookalikes</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-violet-500/20 text-violet-300 font-mono">
              Showing {displayed.length} of {totalQualifying !== undefined ? totalQualifying : filtered.length} qualifying
            </span>
          </h3>
          <p className="text-xs text-slate-400">
            Participant scores aggregated via maximum pose similarity across authorized reference portraits.
          </p>
        </div>

        {/* Filter and Sort Toolbar */}
        <div className="flex items-center gap-2">
          {/* Tier Filter */}
          <div className="flex items-center gap-1 glass-panel px-2.5 py-1 rounded-xl text-xs border border-white/10">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={tierFilter}
              onChange={(e) => setTierFilter(e.target.value)}
              className="bg-transparent text-slate-200 text-xs focus:outline-none cursor-pointer"
            >
              <option value="all" className="bg-midnight-900 text-white">All Tiers</option>
              <option value="remarkable" className="bg-midnight-900 text-white">Remarkable (≥82%)</option>
              <option value="strong" className="bg-midnight-900 text-white">Strong (65-81%)</option>
              <option value="moderate" className="bg-midnight-900 text-white">Moderate (45-64%)</option>
              <option value="subtle" className="bg-midnight-900 text-white">Subtle (&lt;45%)</option>
            </select>
          </div>

          {/* Sort Order */}
          <button
            onClick={() => setSortOrder(sortOrder === "desc" ? "asc" : "desc")}
            className="flex items-center gap-1 glass-panel px-2.5 py-1 rounded-xl text-xs border border-white/10 text-slate-300 hover:text-white cursor-pointer transition-colors"
            title="Toggle sort order"
          >
            <ArrowUpDown className="w-3.5 h-3.5 text-cyan-400" />
            <span>{sortOrder === "desc" ? "Highest First" : "Lowest First"}</span>
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {displayed.map((c) => (
          <div
            key={c.image_id}
            className="glass-panel rounded-2xl border border-white/10 p-4 hover:border-violet-500/40 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="relative aspect-square rounded-xl overflow-hidden bg-slate-900 mb-3">
                <img
                  src={resolveImageUrl(c.image_url)}
                  alt={c.display_name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-2 left-2 bg-midnight-950/80 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-bold text-white border border-white/10">
                  Rank #{c.rank}
                </div>
                <div className="absolute top-2 right-2 bg-violet-600/90 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-bold text-white shadow-glow">
                  {c.resemblance_percentage}%
                </div>
                {c.image_count && c.image_count > 1 && (
                  <div className="absolute bottom-2 left-2 bg-midnight-950/80 backdrop-blur-md px-2 py-0.5 rounded text-[10px] text-slate-300 border border-white/10">
                    {c.image_count} photos
                  </div>
                )}
              </div>

              <h4 className="text-sm font-bold text-white truncate">{c.display_name}</h4>
              <p className="text-xs text-slate-400 truncate mb-1">{c.bio_caption || "Authorized Portrait"}</p>
              <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 mb-3">
                <span>Cosine: {c.similarity_score}</span>
                <span className="text-cyan-400 truncate max-w-[130px]">{c.resemblance_tier}</span>
              </div>
            </div>

            <div className="flex items-center gap-2 pt-2 border-t border-white/10">
              <button
                onClick={() => onOpenSideBySide(c)}
                className="flex-1 py-1.5 rounded-lg glass-panel hover:bg-white/10 text-[11px] font-semibold text-slate-200 transition-colors flex items-center justify-center gap-1 cursor-pointer"
              >
                <Split className="w-3.5 h-3.5 text-cyan-400" />
                <span>Compare</span>
              </button>
              <button
                onClick={() => onOpenShareCard(c)}
                className="p-1.5 rounded-lg glass-panel hover:bg-white/10 text-slate-300 hover:text-white transition-colors cursor-pointer"
                title="Save Result Card"
              >
                <Share2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination / Load More */}
      {displayed.length < sorted.length && (
        <div className="mt-6 text-center">
          <button
            onClick={() => setDisplayCount((prev) => prev + 6)}
            className="px-6 py-2.5 rounded-xl glass-panel border border-white/10 hover:border-violet-500/40 text-xs font-semibold text-slate-200 hover:text-white transition-all cursor-pointer shadow-lg"
          >
            Load More Lookalikes ({sorted.length - displayed.length} remaining)
          </button>
        </div>
      )}
    </div>
  );
};

