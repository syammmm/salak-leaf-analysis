import cv2
import numpy as np


def overlay_colormap_on_image(
    base_rgb,
    colormap_bgr,
    mask,
    alpha=0.6
):
    """
    Overlay colormap on original RGB image using alpha blending.
    """
    base_bgr = cv2.cvtColor(base_rgb, cv2.COLOR_RGB2BGR)

    overlay = base_bgr.copy()

    # hanya area daun
    overlay[mask > 0] = cv2.addWeighted(
        base_bgr[mask > 0],
        1 - alpha,
        colormap_bgr[mask > 0],
        alpha,
        0
    )

    return overlay