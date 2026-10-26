import React, { useState, useRef, useCallback } from "react";
import { Upload, Camera, RefreshCw, AlertCircle, UserCheck, Sparkles, X } from "lucide-react";
import type { FaceBox } from "../types";

interface UploadZoneProps {
  onAnalyze: (file?: File, imageBase64?: string, selectedFaceIndex?: number) => void;
  isLoading: boolean;
  multipleFacesData?: {
    faces: FaceBox[];
    imageSrc: string;
  } | null;
  onClearMultiFace: () => void;
  minThreshold: number;
  onThresholdChange: (val: number) => void;
  maxDisplayCount: number;
  onMaxDisplayCountChange: (val: number) => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onAnalyze,
  isLoading,
  multipleFacesData,
  onClearMultiFace,
  minThreshold,
  onThresholdChange,
  maxDisplayCount,
  onMaxDisplayCountChange,
}) => {
  const [activeMode, setActiveMode] = useState<"upload" | "camera">("upload");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraLoading, setCameraLoading] = useState(false);
  const [consentChecked, setConsentChecked] = useState(true);
  const [dragActive, setDragActive] = useState(false);
  const [errorWarning, setErrorWarning] = useState<string | null>(null);
  const [showConfig, setShowConfig] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Stop camera tracks cleanly on unmount or tab switch
  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
    setCameraLoading(false);
  }, []);

  React.useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  // Handle file select
  const handleFileChange = (file: File) => {
    setErrorWarning(null);
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setErrorWarning("Please upload a valid JPEG, PNG, or WebP photo.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setErrorWarning("Image size exceeds 10MB limit. Please upload a smaller photo.");
      return;
    }

    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    stopCamera();
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  }, []);

  // Ensure video element receives the stream when mounted
  React.useEffect(() => {
    if (isCameraActive && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch((err) => {
        console.warn("video.play() failed:", err);
      });
    }
  }, [isCameraActive]);

  // WebCam handling
  const startCamera = async () => {
    setErrorWarning(null);
    setCameraLoading(true);
    setPreviewUrl(null);
    setSelectedFile(null);

    // Stop existing stream if running
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }

    try {
      let stream: MediaStream;
      try {
        // Preferred high-quality front-facing user camera
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: "user"
          },
          audio: false
        });
      } catch {
        // Fallback to basic video constraint if strict parameters fail
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false
        });
      }

      streamRef.current = stream;
      setIsCameraActive(true);
    } catch (err: any) {
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setErrorWarning("Camera permission denied. Please allow camera access in your browser address bar settings.");
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        setErrorWarning("No camera device was detected on your computer or phone.");
      } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
        setErrorWarning("Camera is in use by another application or locked by the OS.");
      } else {
        setErrorWarning(`Could not start camera: ${err.message || "Unknown error"}`);
      }
      setIsCameraActive(false);
    } finally {
      setCameraLoading(false);
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Draw flipped snapshot matching mirror preview
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    
    const dataUrl = canvas.toDataURL("image/jpeg", 0.95);
    setPreviewUrl(dataUrl);
    stopCamera();
  };

  const retakePhoto = () => {
    setPreviewUrl(null);
    setSelectedFile(null);
    startCamera();
  };

  // Demo presets for 1-click test
  const handleTryPreset = async (imageFilename: string) => {
    setErrorWarning(null);
    try {
      const resp = await fetch(`/api/gallery/images/${imageFilename}`);
      const blob = await resp.blob();
      const file = new File([blob], imageFilename, { type: "image/jpeg" });
      handleFileChange(file);
    } catch {
      setErrorWarning("Could not load preset image.");
    }
  };

  const handleSubmit = () => {
    if (!consentChecked) {
      setErrorWarning("Please check the consent box to authorize ephemeral lookalike matching.");
      return;
    }
    if (selectedFile) {
      onAnalyze(selectedFile, undefined);
    } else if (previewUrl && previewUrl.startsWith("data:")) {
      onAnalyze(undefined, previewUrl);
    } else {
      setErrorWarning("Please select or capture a photo first.");
    }
  };

  return (
    <div id="upload-section" className="max-w-3xl mx-auto px-4 py-8">
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 relative shadow-2xl">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-1 bg-gradient-to-r from-transparent via-violet-500 to-transparent" />

        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-white mb-2">
            {activeMode === "upload" ? "Upload Your Portrait" : "Live Camera Discovery"}
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            {activeMode === "upload"
              ? "For best geometric retrieval, use an upright, evenly lit portrait facing the camera."
              : "Position your face within the canonical oval. Query frames remain in your browser until you search."}
          </p>
        </div>

        {/* Multi-Face Disambiguation Modal Overlay */}
        {multipleFacesData && (
          <div className="mb-6 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-200">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <UserCheck className="w-5 h-5 text-amber-400" />
                <span className="font-semibold text-sm">Multiple Faces Detected ({multipleFacesData.faces.length})</span>
              </div>
              <button onClick={onClearMultiFace} className="text-xs text-slate-400 hover:text-white cursor-pointer">
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-slate-300 mb-3">
              Click on the face you wish to analyze for doppelgänger matching:
            </p>
            <div className="flex flex-wrap gap-2">
              {multipleFacesData.faces.map((f, idx) => (
                <button
                  key={idx}
                  onClick={() => onAnalyze(selectedFile || undefined, previewUrl || undefined, idx)}
                  className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-xs font-medium text-amber-200 transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Analyze Face #{idx + 1} (Conf: {(f.confidence * 100).toFixed(0)}%)</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Upload Mode Switcher Tabs */}
        <div className="flex justify-center gap-3 mb-6">
          <button
            type="button"
            id="tab-upload-mode"
            onClick={() => {
              setActiveMode("upload");
              stopCamera();
            }}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all cursor-pointer ${
              activeMode === "upload"
                ? "bg-violet-600 text-white shadow-glow border border-violet-400/40"
                : "glass-panel text-slate-300 hover:text-white border border-white/10"
            }`}
          >
            <Upload className="w-4 h-4" />
            <span>Upload Image</span>
          </button>

          <button
            type="button"
            id="tab-camera-mode"
            onClick={() => {
              setActiveMode("camera");
              startCamera();
            }}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all cursor-pointer ${
              activeMode === "camera"
                ? "bg-cyan-500 text-midnight-950 shadow-glow-cyan border border-cyan-300 font-extrabold"
                : "glass-panel text-slate-300 hover:text-white border border-white/10"
            }`}
          >
            <Camera className="w-4 h-4" />
            <span>Live Camera</span>
          </button>
        </div>

        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          id="portrait-file-input"
        />

        {/* Display Area: Upload Drag&Drop vs Camera vs Captured Preview */}
        {activeMode === "upload" ? (
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`relative rounded-2xl border-2 border-dashed transition-all duration-300 overflow-hidden flex flex-col items-center justify-center min-h-[300px] ${
              dragActive
                ? "border-violet-500 bg-violet-500/10"
                : previewUrl
                ? "border-white/20 bg-midnight-900"
                : "border-white/10 bg-midnight-900/60 hover:border-violet-500/50 hover:bg-midnight-900/90"
            }`}
          >
            {previewUrl ? (
              <div className="relative w-full h-[320px] bg-black/40 flex items-center justify-center p-4">
                <img
                  src={previewUrl}
                  alt="Selected Portrait Preview"
                  className="max-h-full max-w-full rounded-xl object-contain shadow-lg"
                />
                <button
                  type="button"
                  onClick={() => {
                    setPreviewUrl(null);
                    setSelectedFile(null);
                  }}
                  className="absolute top-4 right-4 p-2 rounded-full bg-midnight-950/80 hover:bg-midnight-900 text-slate-300 hover:text-white border border-white/10 transition-colors cursor-pointer"
                  title="Change Photo"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="p-8 text-center cursor-pointer group"
              >
                <div className="w-16 h-16 rounded-2xl bg-violet-600/10 border border-violet-500/20 text-violet-400 mx-auto flex items-center justify-center mb-4 group-hover:scale-110 group-hover:bg-violet-600/20 transition-all duration-300">
                  <Upload className="w-7 h-7" />
                </div>
                <p className="text-sm font-semibold text-white mb-1">
                  Drag and drop your portrait here
                </p>
                <p className="text-xs text-slate-400 mb-3">
                  or click to select from your device
                </p>
                <span className="inline-block px-2.5 py-1 rounded bg-white/5 text-[11px] text-slate-400 border border-white/5">
                  JPEG, PNG, WebP up to 10MB
                </span>
              </div>
            )}
          </div>
        ) : (
          /* Live Camera View */
          <div className="relative rounded-2xl border border-cyan-500/30 overflow-hidden bg-black flex flex-col items-center justify-center min-h-[320px]">
            {isCameraActive ? (
              <div className="relative w-full h-[360px] bg-black flex items-center justify-center overflow-hidden">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover transform -scale-x-100"
                />
                <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                  <div className="w-52 h-72 border-2 border-cyan-400/60 rounded-[48%] shadow-[0_0_25px_rgba(6,182,212,0.4)] relative">
                    <div className="biometric-scanner-line" />
                    <div className="absolute top-3 left-1/2 -translate-x-1/2 text-[10px] font-mono tracking-widest text-cyan-300/80 uppercase bg-black/60 px-2 py-0.5 rounded">
                      Align Face
                    </div>
                  </div>
                </div>

                <div className="absolute bottom-4 flex items-center gap-3 z-10">
                  <button
                    type="button"
                    id="btn-capture-photo"
                    onClick={capturePhoto}
                    className="px-6 py-2.5 rounded-full bg-cyan-500 hover:bg-cyan-400 text-midnight-950 font-bold text-xs shadow-glow-cyan transition-all flex items-center gap-2 cursor-pointer"
                  >
                    <Camera className="w-4 h-4" />
                    <span>Capture Photo</span>
                  </button>

                  <button
                    type="button"
                    onClick={stopCamera}
                    className="px-4 py-2.5 rounded-full bg-midnight-950/80 hover:bg-midnight-900 text-slate-300 text-xs font-semibold border border-white/10 transition-colors cursor-pointer"
                  >
                    Stop Camera
                  </button>
                </div>
              </div>
            ) : previewUrl ? (
              /* Captured Frame Review */
              <div className="relative w-full h-[360px] bg-black/70 flex flex-col items-center justify-center p-4">
                <img
                  src={previewUrl}
                  alt="Captured Webcam Frame"
                  className="max-h-[260px] rounded-xl object-contain shadow-2xl border border-cyan-500/40"
                />
                <div className="flex items-center gap-3 mt-3">
                  <button
                    type="button"
                    onClick={retakePhoto}
                    className="px-4 py-2 rounded-xl bg-midnight-900 hover:bg-midnight-800 text-slate-200 text-xs font-semibold border border-white/10 flex items-center gap-1.5 cursor-pointer transition-colors"
                  >
                    <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Retake</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={isLoading}
                    className="px-6 py-2 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 text-white font-bold text-xs shadow-glow hover:shadow-cyan-500/30 flex items-center gap-1.5 cursor-pointer transition-all"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
                    <span>Find My Lookalikes</span>
                  </button>
                </div>
              </div>
            ) : (
              /* Camera Ready / Inactive Screen */
              <div className="p-8 text-center">
                <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mx-auto flex items-center justify-center mb-4">
                  <Camera className="w-7 h-7" />
                </div>
                <p className="text-sm font-semibold text-white mb-2">Webcam is paused or not started</p>
                <button
                  type="button"
                  onClick={startCamera}
                  disabled={cameraLoading}
                  className="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-midnight-950 font-bold text-xs shadow-glow-cyan transition-all cursor-pointer"
                >
                  {cameraLoading ? "Requesting Permissions..." : "Start Camera"}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Search Engine Settings & Threshold Calibration (Collapsible) */}
        <div className="mt-4 p-3.5 rounded-2xl bg-white/[0.03] border border-white/5">
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => setShowConfig(!showConfig)}
              className="text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-2 cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Full-Gallery Search Controls & Calibration</span>
              <span className="text-[10px] text-slate-500 font-mono">
                (Min: {minThreshold}%, Max Display: {maxDisplayCount})
              </span>
            </button>
            <button
              type="button"
              onClick={() => setShowConfig(!showConfig)}
              className="text-[11px] text-cyan-400 hover:underline cursor-pointer"
            >
              {showConfig ? "Hide" : "Adjust"}
            </button>
          </div>

          {showConfig && (
            <div className="mt-4 pt-3 border-t border-white/5 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label htmlFor="threshold-slider" className="font-semibold text-slate-300">
                    Min Resemblance Threshold:
                  </label>
                  <span className="font-mono text-cyan-400 font-bold">{minThreshold}%</span>
                </div>
                <input
                  type="range"
                  id="threshold-slider"
                  min="0"
                  max="90"
                  step="5"
                  value={minThreshold}
                  onChange={(e) => onThresholdChange(Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
                <p className="text-[10px] text-slate-500 mt-1">
                  Filters results returning only lookalikes with resemblance ≥ {minThreshold}%. Set to 0% to discover all.
                </p>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label htmlFor="display-limit-input" className="font-semibold text-slate-300">
                    Max Display Results:
                  </label>
                  <span className="font-mono text-violet-400 font-bold">{maxDisplayCount}</span>
                </div>
                <input
                  type="range"
                  id="display-limit-input"
                  min="3"
                  max="50"
                  step="1"
                  value={maxDisplayCount}
                  onChange={(e) => onMaxDisplayCountChange(Number(e.target.value))}
                  className="w-full accent-violet-400 cursor-pointer"
                />
                <p className="text-[10px] text-slate-500 mt-1">
                  Independent of search: searches every participant, but limits cards rendered on screen.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Instant Demo Presets Bar */}
        <div className="mt-4 p-3 rounded-xl bg-white/5 border border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Don't have a photo handy? Test instant demo subjects:</span>
          </div>
          <div className="flex items-center gap-2">
            {[
              { label: "Elena", file: "portrait_elena_1.jpg" },
              { label: "Marcus", file: "portrait_marcus_1.jpg" },
              { label: "Aisha", file: "portrait_aisha_1.jpg" },
            ].map((preset) => (
              <button
                key={preset.label}
                type="button"
                onClick={() => handleTryPreset(preset.file)}
                className="px-2.5 py-1 rounded-lg bg-midnight-900 hover:bg-violet-600/20 border border-white/10 hover:border-violet-500/40 text-[11px] font-medium text-slate-200 transition-colors cursor-pointer"
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        {/* Error / Warning Alert */}
        {errorWarning && (
          <div className="mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorWarning}</span>
          </div>
        )}

        {/* Biometric Privacy Notice Checkbox */}
        <div className="mt-6 flex items-start gap-3 text-left">
          <input
            type="checkbox"
            id="consent-checkbox"
            checked={consentChecked}
            onChange={(e) => setConsentChecked(e.target.checked)}
            className="mt-0.5 w-4 h-4 rounded bg-midnight-900 border-white/20 text-violet-600 focus:ring-violet-500 cursor-pointer"
          />
          <label htmlFor="consent-checkbox" className="text-xs text-slate-300 leading-snug cursor-pointer select-none">
            <span className="font-semibold text-white">Biometric Privacy Agreement:</span> I authorize ephemeral facial feature alignment and embedding generation for lookalike candidate retrieval. Query frames are held strictly in temporary memory and purged immediately after matching.
          </label>
        </div>

        {/* Primary Action Button */}
        <div className="mt-6">
          <button
            type="button"
            id="btn-find-matches-submit"
            onClick={handleSubmit}
            disabled={isLoading || (!selectedFile && !previewUrl)}
            className={`w-full py-4 rounded-xl font-bold text-sm tracking-wide transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer shadow-lg ${
              isLoading || (!selectedFile && !previewUrl)
                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                : "bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 text-white shadow-glow hover:shadow-cyan-500/30 hover:scale-[1.01] active:scale-[0.99]"
            }`}
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Running Full-Gallery Retrieval Pipeline...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-cyan-300" />
                <span>Find My Lookalikes in Full Gallery</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
