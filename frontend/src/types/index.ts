export interface FaceBox {
  box: [number, number, number, number]; // [x, y, w, h]
  confidence: number;
  landmarks: [number, number][]; // 5 points
}

export interface QualityAssessment {
  is_acceptable: boolean;
  overall_quality_score: number;
  sharpness?: number;
  mean_luminance?: number;
  face_area_ratio?: number;
  face_pixel_dimensions?: { width: number; height: number };
  warnings: string[];
}

export interface SubfeatureScore {
  score: number;
  raw_cosine: number;
  label: string;
}

export interface MatchCandidate {
  rank: number;
  participant_id: string;
  display_name: string;
  bio_caption?: string;
  image_id: string;
  image_url: string;
  quality_score: number;
  license_info: string;
  consent_status: string;
  similarity_score: number;
  resemblance_percentage: number;
  resemblance_tier: string;
  badge_color: string;
  description: string;
  subfeature_breakdown?: Record<string, SubfeatureScore>;
  fun_caption?: string;
  image_count?: number;
}

export interface TierCounts {
  exceptional: number;
  strong: number;
  moderate: number;
  subtle: number;
}

export interface SearchStats {
  total_participants_searched: number;
  total_portraits_indexed: number;
  total_qualifying: number;
  resemblance_threshold: number;
  tier_counts: TierCounts;
  detector: string;
  recognition_model: string;
  search_duration_ms: number;
}

export interface MatchResponse {
  request_id: string;
  status: "SUCCESS" | "NO_FACE_DETECTED" | "MULTIPLE_FACES_DETECTED" | "INVALID_IMAGE" | "PROCESSING_ERROR";
  message: string;
  num_faces_detected: number;
  detected_faces?: FaceBox[];
  selected_face_index?: number;
  quality?: QualityAssessment;
  matches: MatchCandidate[];
  stats?: SearchStats;
  model_name: string;
  model_version: string;
  dimension: number;
  execution_latency_ms: number;
}

export interface GalleryImageItem {
  id: string;
  filename: string;
  image_url: string;
  quality_score: number;
  is_primary: boolean;
}

export interface GalleryParticipant {
  id: string;
  display_name: string;
  bio_caption?: string;
  consent_status: string;
  source: string;
  license: string;
  images: GalleryImageItem[];
}

export interface GalleryListResponse {
  total_participants: number;
  total_images: number;
  active_model: string;
  participants: GalleryParticipant[];
}

export interface ModelMetrics {
  model_name: string;
  detector: string;
  dimension: number;
  precision_at_1: number;
  precision_at_5: number;
  recall_at_5: number;
  mean_average_precision: number;
  ndcg_at_5: number;
  mean_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  ranking_stability: number;
  failure_rate: number;
  evaluated_queries_count: number;
  detailed_queries?: any[];
}

export interface EvaluationSummary {
  timestamp: string;
  benchmark_metadata: {
    eval_queries: number;
    relevance_scale: string;
    annotators: number;
    fleiss_kappa: number;
  };
  models: Record<string, ModelMetrics>;
}
