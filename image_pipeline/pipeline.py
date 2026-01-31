from pathlib import Path
import cv2

from image_pipeline.io import load_image_from_bytes
from image_pipeline.preprocessing import preprocess_image
from image_pipeline.segmentation import (
    segment_leaf_hsv,
    extract_main_leaf_center_first,
    apply_mask
)
from image_pipeline.green_indices import compute_exg_gli, compute_exg_map
from image_pipeline.scoring import compute_visual_score

import logging
logger = logging.getLogger("image-pipeline")

def process_leaf_image(
    image_bytes: bytes,
    output_dir: str | None = None
):
    logger.info("Starting image processing")
    # 1) load from memory
    img_rgb = load_image_from_bytes(image_bytes)

    # 2) preprocessing
    img_prep = preprocess_image(img_rgb)

    # 3) segmentation
    mask_green = segment_leaf_hsv(img_prep)
    mask_leaf = extract_main_leaf_center_first(
        img_prep, mask_green, crop_ratio=0.65
    )

    # guard: mask kosong
    if mask_leaf is None or mask_leaf.sum() == 0:
        logger.warning("Segmentation failed: empty mask")
        raise ValueError("Segmentasi gagal. Daun tidak terdeteksi.")
    
    logger.info("Image processing completed successfully")
    leaf_only = apply_mask(img_prep, mask_leaf)

    # 4) indices
    indices = compute_exg_gli(leaf_only, mask_leaf)
    exg_map = compute_exg_map(leaf_only, mask_leaf)

    # 5) scoring
    score = compute_visual_score(indices)

    result = {
        "exg": round(indices["mean_ExG"], 2),
        "gli": round(indices["mean_GLI"], 3),
        "score": score["score"],
        "label": score["label"],
    }

    # 6) optional: save visual output
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        # segmented image
        seg_path = out / "leaf_segmented.png"
        cv2.imwrite(
            str(seg_path),
            cv2.cvtColor(leaf_only, cv2.COLOR_RGB2BGR)
        )

        # ExG map
        exg_path = out / "exg_map.png"
        cv2.imwrite(
            str(exg_path),
            exg_map
        )
        result["segmented_image"] = seg_path.name
        result["exg_image"] = exg_path.name

    return result