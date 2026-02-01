from pathlib import Path
import cv2

from image_pipeline.io import load_image_from_bytes
from image_pipeline.preprocessing import preprocess_image
from image_pipeline.segmentation import (
    segment_leaf_hsv,
    extract_main_leaf_center_first,
    apply_mask
)
from image_pipeline.green_indices import compute_exg_gli, compute_exg_map, compute_gli_map, extract_exg_gli_values
from image_pipeline.scoring import compute_visual_score
from image_pipeline.analysis import save_histogram
from image_pipeline.visualization import overlay_colormap_on_image
from image_pipeline.zonal import (
    create_geometric_zones
)
from image_pipeline.zonal_stats import zonal_stats_exg_gli

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
    gli_map = compute_gli_map(img_prep, mask_leaf)

    # Overlay
    exg_overlay = overlay_colormap_on_image(
        img_prep, exg_map, mask_leaf, alpha=0.6
    )

    gli_overlay = overlay_colormap_on_image(
        img_prep, gli_map, mask_leaf, alpha=0.6
    )
    
    # === ZONAL MASKS ===
    mask_center, mask_ring, mask_edge = create_geometric_zones(mask_leaf)

    # === ZONAL STATISTICS ===
    zonal_stats = zonal_stats_exg_gli(
        img_prep,
        mask_center,
        mask_ring,
        mask_edge
    )
    print("Zonal Statistics:", zonal_stats)
    # 5) scoring
    score = compute_visual_score(indices)

    # extract values for histogram
    exg_vals, gli_vals = extract_exg_gli_values(img_prep, mask_leaf)

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

        # save histograms
        exg_hist = save_histogram(
            exg_vals,
            title="Histogram Excess Green (ExG)",
            filename="hist_exg.png",
            output_dir=out
        )

        gli_hist = save_histogram(
            gli_vals,
            title="Histogram Green Leaf Index (GLI)",
            filename="hist_gli.png",
            output_dir=out
        )

        # GLI map
        gli_path = out / "gli_map.png"
        cv2.imwrite(
            str(out / "gli_map.png"),
            gli_map
        )
        # overlays
        exg_overlay_path = out / "exg_overlay.png"
        cv2.imwrite(str(out / "exg_overlay.png"), exg_overlay)

        gli_overlay_path = out / "gli_overlay.png"
        cv2.imwrite(str(out / "gli_overlay.png"), gli_overlay)

        # result["segmented_image"] = seg_path.name
        # result["exg_image"] = exg_path.name
        # result["gli_image"] = gli_path.name
        # result["hist_exg"] = exg_hist
        # result["hist_gli"] = gli_hist
        # result["exg_overlay"] = exg_overlay_path.name
        # result["gli_overlay"] = gli_overlay_path.name
        
        result.update({
            "segmented_image": seg_path.name,
            "exg_image": exg_path.name,
            "gli_image": gli_path.name,
            "hist_exg": exg_hist,
            "hist_gli": gli_hist,
            "exg_overlay": exg_overlay_path.name,
            "gli_overlay": gli_overlay_path.name,
            "zonal_stats": zonal_stats
        })


    return result