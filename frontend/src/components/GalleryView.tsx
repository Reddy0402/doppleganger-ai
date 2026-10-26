import React, { useState, useEffect } from "react";
import { Database, Search, ShieldCheck, User, RefreshCw, Layers } from "lucide-react";
import type { GalleryParticipant } from "../types";
import { fetchGallery, fetchGalleryStats, reindexGallery, resolveImageUrl } from "../services/api";

export const GalleryView: React.FC = () => {
  const [participants, setParticipants] = useState<GalleryParticipant[]>([]);
  const [stats, setStats] = useState<{ unique_participants: number; indexed_portraits: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [reindexing, setReindexing] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const loadData = async () => {
    setLoading(true);
    try {
      const PAGE_SIZE = 100;
      const [first, statsData] = await Promise.all([
        fetchGallery(1, PAGE_SIZE),
        fetchGalleryStats().catch(() => null)
      ]);
      // Pull the remaining pages so every participant is shown, not just the first page
      const pageCount = Math.ceil(first.total_participants / PAGE_SIZE);
      const rest = await Promise.all(
        Array.from({ length: Math.max(0, pageCount - 1) }, (_, i) => fetchGallery(i + 2, PAGE_SIZE))
      );
      setParticipants([first, ...rest].flatMap((page) => page.participants || []));
      if (statsData) setStats(statsData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleReindex = async () => {
    setReindexing(true);
    try {
      await reindexGallery();
      await loadData();
    } catch (err) {
      console.error("Reindex error:", err);
    } finally {
      setReindexing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filtered = participants.filter((p) =>
    p.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (p.bio_caption && p.bio_caption.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Database className="w-5 h-5 text-cyan-400" />
            <h2 className="text-2xl font-bold text-white">Authorized Portrait Gallery</h2>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Consented reference cohort indexed in the 128D deep vector space.
          </p>
        </div>

        {/* Search Input & Reindex Button */}
        <div className="flex items-center gap-3">
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search participants..."
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-midnight-900 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 transition-colors"
            />
          </div>

          <button
            onClick={handleReindex}
            disabled={reindexing}
            className="px-3 py-2 rounded-xl glass-panel hover:bg-white/10 border border-white/10 text-xs font-semibold text-cyan-300 flex items-center gap-1.5 cursor-pointer transition-colors shadow"
            title="Re-scan and rebuild gallery vector index"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reindexing ? "animate-spin text-cyan-400" : ""}`} />
            <span>{reindexing ? "Indexing..." : "Reindex"}</span>
          </button>
        </div>
      </div>

      {/* Cohort Stats Banner */}
      {stats && (
        <div className="mb-6 p-4 rounded-2xl glass-panel border border-white/5 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-violet-400" />
              <span className="text-slate-400">Unique Participants:</span>
              <span className="font-bold text-white font-mono">{stats.unique_participants}</span>
            </div>
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              <span className="text-slate-400">Total Indexed Portraits:</span>
              <span className="font-bold text-white font-mono">{stats.indexed_portraits}</span>
            </div>
          </div>
          <div className="text-[11px] text-slate-500">
            Deduplicated search aggregates multiple poses to each unique identity.
          </div>
        </div>
      )}

      {loading ? (
        <div className="p-12 text-center text-slate-400">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-cyan-400 mb-2" />
          <p className="text-xs">Loading authorized portrait catalog...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl text-slate-400">
          <User className="w-8 h-8 mx-auto text-slate-600 mb-2" />
          <p className="text-sm">No matching gallery participants found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((p) => {
            const primaryImg = p.images.find((i) => i.is_primary) || p.images[0];
            return (
              <div
                key={p.id}
                className="glass-panel rounded-2xl border border-white/10 overflow-hidden hover:border-violet-500/40 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="relative aspect-square overflow-hidden bg-slate-900">
                    {primaryImg ? (
                      <img
                        src={resolveImageUrl(primaryImg.image_url)}
                        alt={p.display_name}
                        loading="lazy"
                        className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="flex items-center justify-center h-full text-slate-600 text-xs">No Image</div>
                    )}
                    <div className="absolute top-3 left-3 bg-midnight-950/80 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-mono text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                      <ShieldCheck className="w-3 h-3 text-cyan-400" />
                      <span>{p.consent_status}</span>
                    </div>

                    <div className="absolute top-3 right-3 bg-midnight-950/80 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-mono text-slate-300 border border-white/10">
                      {p.license}
                    </div>
                  </div>

                  <div className="p-4">
                    <h3 className="text-sm font-bold text-white mb-0.5">{p.display_name}</h3>
                    <p className="text-xs text-slate-400 line-clamp-2 mb-3">
                      {p.bio_caption || "Certified portrait subject"}
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono border-t border-white/5 pt-2">
                      <span>Source: {p.source}</span>
                      <span>Images: {p.images.length}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
