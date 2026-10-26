import React, { useRef, useState, useEffect } from "react";
import { X, Download, Sparkles } from "lucide-react";
import type { MatchCandidate } from "../types";

interface ShareCardModalProps {
  candidate: MatchCandidate | null;
  userImageSrc?: string;
  onClose: () => void;
}

export const ShareCardModal: React.FC<ShareCardModalProps> = ({
  candidate,
  userImageSrc,
  onClose,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [downloadReady, setDownloadReady] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!candidate || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas resolution (1200 x 630 landscape social card)
    canvas.width = 1200;
    canvas.height = 630;

    // Draw dark background gradient
    const bgGrad = ctx.createLinearGradient(0, 0, 1200, 630);
    bgGrad.addColorStop(0, "#07090E");
    bgGrad.addColorStop(0.5, "#0E1322");
    bgGrad.addColorStop(1, "#07090E");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, 1200, 630);

    // Accent glow orbs
    ctx.beginPath();
    ctx.arc(200, 150, 180, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(139, 92, 246, 0.15)";
    ctx.fill();

    ctx.beginPath();
    ctx.arc(1000, 480, 220, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(6, 182, 212, 0.12)";
    ctx.fill();

    // Border
    ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
    ctx.lineWidth = 4;
    ctx.strokeRect(20, 20, 1160, 590);

    // Header branding
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "bold 34px sans-serif";
    ctx.fillText("Doppelgänger AI", 60, 80);

    ctx.fillStyle = "#06B6D4";
    ctx.font = "600 18px sans-serif";
    ctx.fillText("PERCEPTUAL FACE RESEMBLANCE VERIFIED", 60, 110);

    // Score Callout
    ctx.fillStyle = "#8B5CF6";
    ctx.font = "bold 72px sans-serif";
    ctx.fillText(`${candidate.resemblance_percentage}%`, 60, 220);

    ctx.fillStyle = "#E2E8F0";
    ctx.font = "600 24px sans-serif";
    ctx.fillText(candidate.resemblance_tier, 60, 260);

    ctx.fillStyle = "#94A3B8";
    ctx.font = "normal 18px sans-serif";
    ctx.fillText(`Matched Candidate: ${candidate.display_name}`, 60, 300);

    // Algorithmic Caption
    if (candidate.fun_caption) {
      ctx.fillStyle = "#CBD5E1";
      ctx.font = "italic 18px sans-serif";
      ctx.fillText(`"${candidate.fun_caption.slice(0, 70)}..."`, 60, 350);
    }

    // Disclaimer
    ctx.fillStyle = "#64748B";
    ctx.font = "14px sans-serif";
    ctx.fillText("Private Client-Side Rendering • Evaluated with ArcFace Embeddings • No Genetic Relationship Implied", 60, 570);

    // Load Candidate Image
    const candImg = new Image();
    candImg.crossOrigin = "anonymous";
    candImg.src = candidate.image_url;
    candImg.onload = () => {
      ctx.save();
      ctx.beginPath();
      ctx.roundRect(750, 80, 380, 380, 24);
      ctx.clip();
      ctx.drawImage(candImg, 750, 80, 380, 380);
      ctx.restore();

      ctx.strokeStyle = "rgba(139, 92, 246, 0.5)";
      ctx.lineWidth = 4;
      ctx.strokeRect(750, 80, 380, 380);

      ctx.fillStyle = "#FFFFFF";
      ctx.font = "bold 20px sans-serif";
      ctx.fillText(candidate.display_name, 750, 495);

      ctx.fillStyle = "#94A3B8";
      ctx.font = "15px sans-serif";
      ctx.fillText(candidate.license_info, 750, 520);

      const url = canvas.toDataURL("image/png");
      setDownloadUrl(url);
      setDownloadReady(true);
    };
  }, [candidate, userImageSrc]);

  if (!candidate) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
      <div className="glass-panel w-full max-w-2xl rounded-3xl border border-white/20 p-6 sm:p-8 shadow-2xl relative text-center">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full glass-panel text-slate-300 hover:text-white transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center justify-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xl font-bold text-white">Your Doppelgänger Match Card</h3>
        </div>
        <p className="text-xs text-slate-400 mb-6">
          Rendered directly in your browser. No private photo data is saved to external servers.
        </p>

        {/* Canvas Display */}
        <div className="rounded-2xl overflow-hidden border border-white/10 shadow-2xl mb-6 bg-midnight-950">
          <canvas ref={canvasRef} className="w-full h-auto object-contain" />
        </div>

        {/* Download Action */}
        <div className="flex justify-center gap-4">
          {downloadReady && downloadUrl ? (
            <a
              href={downloadUrl}
              download={`doppelganger-match-${candidate.display_name.toLowerCase().replace(/\s+/g, "-")}.png`}
              className="px-8 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 text-white font-bold text-xs shadow-glow flex items-center gap-2 hover:scale-105 transition-all cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Download PNG Card</span>
            </a>
          ) : (
            <button disabled className="px-6 py-3 rounded-xl bg-slate-800 text-slate-500 text-xs font-semibold">
              Generating High-Res Card...
            </button>
          )}

          <button
            onClick={onClose}
            className="px-6 py-3 rounded-xl glass-panel text-slate-300 hover:text-white text-xs font-semibold cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
