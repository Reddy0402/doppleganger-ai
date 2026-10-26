import { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { LandingHero } from "./components/LandingHero";
import { UploadZone } from "./components/UploadZone";
import { AnalysisProgress } from "./components/AnalysisProgress";
import { MainMatchCard } from "./components/MainMatchCard";
import { TopCandidatesGrid } from "./components/TopCandidatesGrid";
import { SideBySideModal } from "./components/SideBySideModal";
import { ShareCardModal } from "./components/ShareCardModal";
import { GalleryView } from "./components/GalleryView";
import { EvaluationView } from "./components/EvaluationView";
import { PrivacyModal } from "./components/PrivacyModal";
import { fetchHealth, selectModel, findMatches, deleteUpload } from "./services/api";
import type { MatchResponse, MatchCandidate, FaceBox } from "./types";
import { AlertCircle, CheckCircle2 } from "lucide-react";

export function App() {
  const [activeTab, setActiveTab] = useState<"match" | "gallery" | "evaluation" | "privacy">("match");
  const [activeModel, setActiveModel] = useState("sface");
  const [apiOnline, setApiOnline] = useState(false);
  const [galleryCount, setGalleryCount] = useState(0);

  const [isLoading, setIsLoading] = useState(false);
  const [matchResponse, setMatchResponse] = useState<MatchResponse | null>(null);
  const [userImageSrc, setUserImageSrc] = useState<string | undefined>(undefined);
  const [lastUploadedFile, setLastUploadedFile] = useState<File | undefined>(undefined);
  const [lastImageBase64, setLastImageBase64] = useState<string | undefined>(undefined);

  const [multipleFacesData, setMultipleFacesData] = useState<{
    faces: FaceBox[];
    imageSrc: string;
  } | null>(null);

  const [selectedCandidate, setSelectedCandidate] = useState<MatchCandidate | null>(null);
  const [isSideBySideOpen, setIsSideBySideOpen] = useState(false);
  const [isShareCardOpen, setIsShareCardOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

  const showToast = (text: string, type: "success" | "error" = "success") => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Check health
  useEffect(() => {
    const checkApi = async () => {
      try {
        const health = await fetchHealth();
        setApiOnline(true);
        setGalleryCount(health.gallery_portraits_count || 0);
        if (health.active_model) {
          setActiveModel(health.active_model);
        }
      } catch {
        setApiOnline(false);
      }
    };
    checkApi();
    const interval = setInterval(checkApi, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectModel = async (newModel: string) => {
    try {
      await selectModel(newModel);
      setActiveModel(newModel);
      showToast(`Active model switched to ${newModel === "sface" ? "SFace (ArcFace)" : "Spatial Baseline"}`);
    } catch {
      showToast("Failed to switch model", "error");
    }
  };

  const [minThreshold, setMinThreshold] = useState<number>(0);
  const [maxDisplayCount, setMaxDisplayCount] = useState<number>(20);

  const handleAnalyze = async (file?: File, imageBase64?: string, selectedFaceIndex?: number) => {
    setIsLoading(true);
    setMultipleFacesData(null);

    // Save image source for preview
    if (file) {
      setLastUploadedFile(file);
      setUserImageSrc(URL.createObjectURL(file));
    } else if (imageBase64) {
      setLastImageBase64(imageBase64);
      setUserImageSrc(imageBase64);
    }

    try {
      const resp = await findMatches({
        file: file || lastUploadedFile,
        imageBase64: imageBase64 || lastImageBase64,
        topK: maxDisplayCount,
        minThreshold: minThreshold,
        selectedFaceIndex,
        aggregationPolicy: "max",
      });

      if (resp.status === "MULTIPLE_FACES_DETECTED" && resp.detected_faces && resp.detected_faces.length > 1) {
        setMultipleFacesData({
          faces: resp.detected_faces,
          imageSrc: userImageSrc || "",
        });
        showToast("Multiple faces detected. Please select which face to analyze.", "error");
      } else if (resp.status === "NO_FACE_DETECTED") {
        showToast(resp.message || "No face detected. Please try another photo.", "error");
        setMatchResponse(resp);
      } else if (resp.status === "SUCCESS") {
        setMatchResponse(resp);
        if (resp.matches.length > 0) {
          showToast(`Full-gallery search complete! ${resp.stats?.total_qualifying || resp.matches.length} lookalikes found.`);
        } else {
          showToast(`Search complete: 0 lookalikes met the ${minThreshold}% threshold.`);
        }
        setTimeout(() => {
          document.getElementById("results-section")?.scrollIntoView({ behavior: "smooth" });
        }, 100);
      } else {
        showToast(resp.message || "Could not complete match analysis", "error");
      }
    } catch (e: any) {
      showToast(e.message || "Analysis error occurred", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const handlePurgeData = async () => {
    if (matchResponse?.request_id) {
      try {
        await deleteUpload(matchResponse.request_id);
      } catch {}
    }
    setMatchResponse(null);
    setUserImageSrc(undefined);
    setLastUploadedFile(undefined);
    setLastImageBase64(undefined);
    setMultipleFacesData(null);
    showToast("Session upload purged immediately from memory.");
  };

  const handleRetry = () => {
    setMatchResponse(null);
    setUserImageSrc(undefined);
    setLastUploadedFile(undefined);
    setLastImageBase64(undefined);
    setMultipleFacesData(null);
    document.getElementById("upload-section")?.scrollIntoView({ behavior: "smooth" });
  };

  const handleHeroStart = () => {
    setActiveTab("match");
    document.getElementById("upload-section")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-midnight-950 text-slate-100 flex flex-col">
      {/* Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activeModel={activeModel}
        onSelectModel={handleSelectModel}
        galleryCount={galleryCount}
        apiOnline={apiOnline}
      />

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 animate-bounce">
          <div
            className={`px-4 py-3 rounded-2xl glass-panel shadow-2xl flex items-center gap-2.5 text-xs font-semibold ${
              toastMessage.type === "success"
                ? "border-emerald-500/40 text-emerald-300"
                : "border-rose-500/40 text-rose-300"
            }`}
          >
            {toastMessage.type === "success" ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-400" />
            )}
            <span>{toastMessage.text}</span>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1">
        {activeTab === "match" && (
          <>
            <LandingHero
              onStart={handleHeroStart}
              onExploreGallery={() => setActiveTab("gallery")}
            />

            <UploadZone
              onAnalyze={handleAnalyze}
              isLoading={isLoading}
              multipleFacesData={multipleFacesData}
              onClearMultiFace={() => setMultipleFacesData(null)}
              minThreshold={minThreshold}
              onThresholdChange={setMinThreshold}
              maxDisplayCount={maxDisplayCount}
              onMaxDisplayCountChange={setMaxDisplayCount}
            />

            <AnalysisProgress isLoading={isLoading} />

            {/* Zero Qualifying Matches State */}
            {matchResponse && matchResponse.status === "SUCCESS" && matchResponse.matches.length === 0 && (
              <div id="results-section" className="max-w-2xl mx-auto px-4 py-8 text-center">
                <div className="glass-panel p-8 rounded-3xl border border-white/10 shadow-2xl">
                  <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mx-auto flex items-center justify-center mb-3">
                    <AlertCircle className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">No Matches Met Resemblance Threshold</h3>
                  <p className="text-xs sm:text-sm text-slate-400 mb-4 leading-relaxed">
                    Searched across all {matchResponse.stats?.total_participants_searched || galleryCount} unique participants, but none exceeded your configured minimum threshold of {matchResponse.stats?.resemblance_threshold || minThreshold}%.
                  </p>
                  <button
                    onClick={() => {
                      setMinThreshold(0);
                      handleAnalyze();
                    }}
                    className="px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-bold text-xs shadow-glow transition-all cursor-pointer"
                  >
                    Lower Threshold to 0% & Search Again
                  </button>
                </div>
              </div>
            )}

            {/* Results Display */}
            {matchResponse && matchResponse.status === "SUCCESS" && matchResponse.matches.length > 0 && (
              <div id="results-section">
                <MainMatchCard
                  topMatch={matchResponse.matches[0]}
                  userImageSrc={userImageSrc}
                  quality={matchResponse.quality}
                  stats={matchResponse.stats}
                  modelName={matchResponse.model_name}
                  dimension={matchResponse.dimension}
                  latencyMs={matchResponse.execution_latency_ms}
                  onOpenSideBySide={(c) => {
                    setSelectedCandidate(c);
                    setIsSideBySideOpen(true);
                  }}
                  onOpenShareCard={(c) => {
                    setSelectedCandidate(c);
                    setIsShareCardOpen(true);
                  }}
                  onPurgeData={handlePurgeData}
                  onRetry={handleRetry}
                />

                <TopCandidatesGrid
                  candidates={matchResponse.matches}
                  totalQualifying={matchResponse.stats?.total_qualifying}
                  onOpenSideBySide={(c) => {
                    setSelectedCandidate(c);
                    setIsSideBySideOpen(true);
                  }}
                  onOpenShareCard={(c) => {
                    setSelectedCandidate(c);
                    setIsShareCardOpen(true);
                  }}
                />
              </div>
            )}
          </>
        )}

        {activeTab === "gallery" && (
          <GalleryView />
        )}

        {activeTab === "evaluation" && (
          <EvaluationView />
        )}

        {activeTab === "privacy" && (
          <PrivacyModal onPurge={handlePurgeData} />
        )}
      </main>

      {/* Fullscreen Side-by-Side Modal */}
      {isSideBySideOpen && (
        <SideBySideModal
          candidate={selectedCandidate}
          userImageSrc={userImageSrc}
          onClose={() => setIsSideBySideOpen(false)}
        />
      )}

      {/* Client-Side Share Card Modal */}
      {isShareCardOpen && (
        <ShareCardModal
          candidate={selectedCandidate}
          userImageSrc={userImageSrc}
          onClose={() => setIsShareCardOpen(false)}
        />
      )}

      {/* Footer */}
      <footer className="glass-panel border-t border-white/5 py-8 px-4 text-center text-xs text-slate-500 mt-12">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-display font-bold text-white">Doppelgänger AI</span>
            <span>&bull;</span>
            <span>Pretrained ArcFace & YuNet Geometric Vision Engine</span>
          </div>

          <div className="flex items-center gap-4 text-slate-400">
            <button onClick={() => setActiveTab("privacy")} className="hover:text-white transition-colors cursor-pointer">
              Privacy Architecture
            </button>
            <button onClick={() => setActiveTab("evaluation")} className="hover:text-white transition-colors cursor-pointer">
              Benchmark Metrics
            </button>
            <button onClick={() => setActiveTab("gallery")} className="hover:text-white transition-colors cursor-pointer">
              Authorized Cohort
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
