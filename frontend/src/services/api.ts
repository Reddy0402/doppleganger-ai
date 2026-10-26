import type { MatchResponse, GalleryListResponse, EvaluationSummary } from "../types";

const API_HOST = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const API_BASE = `${API_HOST}/api`;

export function resolveImageUrl(url?: string): string {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:")) return url;
  if (url.startsWith("/")) return `${API_HOST}${url}`;
  return `${API_BASE}/${url}`;
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function fetchModels() {
  const res = await fetch(`${API_BASE}/models`);
  if (!res.ok) throw new Error("Failed to load models");
  return res.json();
}

export async function selectModel(modelName: string) {
  const formData = new FormData();
  formData.append("model_name", modelName);
  const res = await fetch(`${API_BASE}/models/select`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to switch model");
  return res.json();
}

export async function findMatches(params: {
  file?: File;
  imageBase64?: string;
  topK?: number;
  minThreshold?: number;
  selectedFaceIndex?: number;
  aggregationPolicy?: string;
}): Promise<MatchResponse> {
  const formData = new FormData();
  if (params.file) {
    formData.append("file", params.file);
  }
  if (params.imageBase64) {
    formData.append("image_base64", params.imageBase64);
  }
  if (params.topK !== undefined) {
    formData.append("top_k", params.topK.toString());
  }
  if (params.minThreshold !== undefined) {
    formData.append("min_threshold", params.minThreshold.toString());
  }
  if (params.selectedFaceIndex !== undefined) {
    formData.append("selected_face_index", params.selectedFaceIndex.toString());
  }
  if (params.aggregationPolicy) {
    formData.append("aggregation_policy", params.aggregationPolicy);
  }

  const res = await fetch(`${API_BASE}/matches`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Error querying doppelgänger matches");
  }

  return res.json();
}

export async function fetchGallery(page: number = 1, pageSize: number = 50): Promise<GalleryListResponse> {
  const res = await fetch(`${API_BASE}/gallery?page=${page}&page_size=${pageSize}`);
  if (!res.ok) throw new Error("Failed to fetch gallery");
  return res.json();
}

export async function fetchGalleryStats() {
  const res = await fetch(`${API_BASE}/gallery/stats`);
  if (!res.ok) throw new Error("Failed to fetch gallery stats");
  return res.json();
}

export async function reindexGallery() {
  const res = await fetch(`${API_BASE}/gallery/reindex`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to reindex gallery");
  return res.json();
}

export async function deleteUpload(uploadId: string) {
  const res = await fetch(`${API_BASE}/uploads/${uploadId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to purge session data");
  return res.json();
}

export async function fetchEvaluationSummary(): Promise<EvaluationSummary> {
  const res = await fetch(`${API_BASE}/evaluation/summary`);
  if (!res.ok) throw new Error("Failed to fetch evaluation metrics");
  return res.json();
}
