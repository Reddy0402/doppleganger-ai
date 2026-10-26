import cv2
import numpy as np
from typing import Dict, Any, List

def compute_blur_score(image_rgb: np.ndarray) -> float:
    """
    Computes the variance of the Laplacian of the grayscale image.
    Higher values indicate greater sharpness; lower values indicate blur.
    """
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = float(laplacian.var())
    return variance

def compute_exposure_metrics(image_rgb: np.ndarray) -> Dict[str, float]:
    """
    Evaluates exposure balance by analyzing luminance distribution.
    """
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))
    
    # Check clipping at extremes
    under_ratio = float(np.sum(gray < 15) / gray.size)
    over_ratio = float(np.sum(gray > 240) / gray.size)
    
    return {
        "mean_luminance": mean_val,
        "std_luminance": std_val,
        "underexposed_ratio": under_ratio,
        "overexposed_ratio": over_ratio
    }

def assess_face_quality(
    image_rgb: np.ndarray,
    face_box: List[int],
    blur_threshold: float = 60.0
) -> Dict[str, Any]:
    """
    Assess overall facial crop quality.
    face_box format: [x, y, w, h]
    """
    h_img, w_img = image_rgb.shape[:2]
    x, y, w, h = face_box
    
    # Clip coordinates to image boundary
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(w_img, x + w)
    y2 = min(h_img, y + h)
    
    face_crop = image_rgb[y1:y2, x1:x2]
    if face_crop.size == 0 or face_crop.shape[0] < 10 or face_crop.shape[1] < 10:
        return {
            "is_acceptable": False,
            "overall_quality_score": 0.0,
            "warnings": ["Face region is too small or invalid."]
        }
    
    # Sharpness on face crop
    face_sharpness = compute_blur_score(face_crop)
    exposure = compute_exposure_metrics(face_crop)
    
    # Face coverage
    face_area = w * h
    img_area = w_img * h_img
    area_ratio = face_area / max(1, img_area)
    
    warnings = []
    
    # Evaluate blur
    if face_sharpness < blur_threshold:
        warnings.append("Image appears blurry or out of focus. A sharper photo produces better lookalike results.")
        
    # Evaluate exposure
    if exposure["mean_luminance"] < 45 or exposure["underexposed_ratio"] > 0.35:
        warnings.append("Low lighting detected. Try uploading an image with more even, natural illumination.")
    elif exposure["mean_luminance"] > 215 or exposure["overexposed_ratio"] > 0.35:
        warnings.append("Image is overexposed or washed out. Try avoiding harsh direct flash.")
        
    # Evaluate face size
    if min(w, h) < 60:
        warnings.append("Face resolution is very small. A closer portrait will improve embedding precision.")

    # Quality score (0.0 to 1.0)
    sharpness_factor = min(1.0, face_sharpness / 200.0)
    exp_factor = 1.0 - (exposure["underexposed_ratio"] + exposure["overexposed_ratio"])
    exp_factor = max(0.0, min(1.0, exp_factor))
    size_factor = min(1.0, min(w, h) / 120.0)
    
    composite_score = round(0.4 * sharpness_factor + 0.35 * exp_factor + 0.25 * size_factor, 3)
    is_acceptable = composite_score >= 0.25 and min(w, h) >= 40
    
    return {
        "is_acceptable": is_acceptable,
        "overall_quality_score": composite_score,
        "sharpness": round(face_sharpness, 1),
        "mean_luminance": round(exposure["mean_luminance"], 1),
        "face_area_ratio": round(area_ratio, 3),
        "face_pixel_dimensions": {"width": w, "height": h},
        "warnings": warnings
    }
