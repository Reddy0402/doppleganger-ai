import React from "react";
import { ShieldCheck, Lock, Trash2, EyeOff, Server, FileCheck } from "lucide-react";

interface PrivacyModalProps {
  onClose?: () => void;
  onPurge?: () => void;
}

export const PrivacyModal: React.FC<PrivacyModalProps> = ({ onPurge }) => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 shadow-2xl relative">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Biometric Privacy & Data Architecture</h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Ethical standards, zero persistent storage, and ephemeral memory management.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
          <div className="p-4 rounded-xl bg-midnight-900 border border-white/5">
            <div className="flex items-center gap-2 text-sm font-bold text-white mb-1">
              <Lock className="w-4 h-4 text-emerald-400" />
              <span>Zero Persistent Selfie Storage</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Selfies and camera captures are processed in volatile memory. If temporary scratch files are generated during decompression, they are strictly purged inside Python finally blocks and background sweepers.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-midnight-900 border border-white/5">
            <div className="flex items-center gap-2 text-sm font-bold text-white mb-1">
              <EyeOff className="w-4 h-4 text-cyan-400" />
              <span>No Embedding Harvesting</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Your 128D query vector is computed strictly for real-time similarity search. It is never appended to the gallery index or stored in the database.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-midnight-900 border border-white/5">
            <div className="flex items-center gap-2 text-sm font-bold text-white mb-1">
              <Server className="w-4 h-4 text-violet-400" />
              <span>Client-Side Card Rendering</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              When you download or share your result card, it is rendered on an HTML5 canvas directly in your web browser. No private photo is transmitted to external card generation APIs.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-midnight-900 border border-white/5">
            <div className="flex items-center gap-2 text-sm font-bold text-white mb-1">
              <FileCheck className="w-4 h-4 text-amber-400" />
              <span>Certified Consent Gallery</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every portrait in our reference gallery has documented license provenance (CC0-1.0 or explicit participant consent). No unauthorized social media scraping is permitted.
            </p>
          </div>
        </div>

        {/* Action button */}
        {onPurge && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex flex-col sm:flex-row items-center justify-between gap-3 mt-6">
            <div>
              <h4 className="text-xs font-bold text-rose-300">Instant Session Purge</h4>
              <p className="text-[11px] text-slate-400">
                Immediately trigger backend garbage collection and wipe any active session buffers.
              </p>
            </div>
            <button
              onClick={onPurge}
              className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer shrink-0"
            >
              <Trash2 className="w-4 h-4" />
              <span>Purge Active Session Data</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
