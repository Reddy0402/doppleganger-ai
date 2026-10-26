import cv2
import numpy as np
from typing import List, Optional

# Canonical 5-point reference coordinates for 112x112 ArcFace alignment
REFERENCE_LANDMARKS_112 = np.array([
    [38.2946, 51.6963],  # right eye center
    [73.5318, 51.5014],  # left eye center
    [56.0252, 71.7366],  # nose tip
    [41.5493, 92.3655],  # right mouth corner
    [70.7299, 92.2041]   # left mouth corner
], dtype=np.float32)

def align_face_5point(
    image_rgb: np.ndarray,
    landmarks: List[List[float]],
    output_size: int = 112
) -> np.ndarray:
    """
    Align face image using 5-point similarity transformation matrix.
    Produces a canonically centered, upright 112x112 face crop.
    """
    src_pts = np.array(landmarks, dtype=np.float32)
    dst_pts = REFERENCE_LANDMARKS_112.copy()
    
    if output_size != 112:
        dst_pts = dst_pts * (output_size / 112.0)

    # Estimate similarity transform (rotation, translation, uniform scale)
    M, _ = cv2.estimateAffinePartial2D(src_pts, dst_pts, method=cv2.LMEDS)
    if M is None:
        # Fallback to bounding box crop if affine estimation fails
        x_min = max(0, int(np.min(src_pts[:, 0])))
        y_min = max(0, int(np.min(src_pts[:, 1])))
        x_max = min(image_rgb.shape[1], int(np.max(src_pts[:, 0])))
        y_max = min(image_rgb.shape[0], int(np.max(src_pts[:, 1])))
        crop = image_rgb[y_min:y_max, x_min:x_max]
        if crop.size == 0:
            return cv2.resize(image_rgb, (output_size, output_size))
        return cv2.resize(crop, (output_size, output_size))

    aligned_crop = cv2.warpAffine(
        image_rgb,
        M,
        (output_size, output_size),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101
    )
    return aligned_crop
