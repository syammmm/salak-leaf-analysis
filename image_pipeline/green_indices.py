import numpy as np
import cv2

def compute_exg_map(img_rgb, mask):
    """
    Generate Excess Green (ExG) heatmap image.
    """
    img = img_rgb.astype(np.float32)

    R = img[:, :, 0]
    G = img[:, :, 1]
    B = img[:, :, 2]

    exg = 2 * G - R - B

    # set background to NaN agar tidak ikut
    exg[mask == 0] = np.nan

    # normalize ExG to 0–255
    exg_min = np.nanmin(exg)
    exg_max = np.nanmax(exg)

    exg_norm = (exg - exg_min) / (exg_max - exg_min + 1e-6)
    exg_norm = (exg_norm * 255).astype(np.uint8)

    # apply colormap
    # exg_colormap = cv2.applyColorMap(exg_norm, cv2.COLORMAP_RDYLGN)
    exg_colormap = cv2.applyColorMap(exg_norm, cv2.COLORMAP_TURBO)


    return exg_colormap


def compute_exg_gli(img_rgb, mask):
    pixels = img_rgb[mask > 0].astype(np.float32)

    if pixels.size == 0:
        raise ValueError("Segmentasi gagal. Daun tidak terdeteksi.")

    R = pixels[:, 0]
    G = pixels[:, 1]
    B = pixels[:, 2]

    ExG = 2*G - R - B
    GLI = (2*G - R - B) / (2*G + R + B + 1e-6)

    return {
        "mean_ExG": np.mean(ExG),
        "std_ExG": np.std(ExG),
        "mean_GLI": np.mean(GLI),
        "std_GLI": np.std(GLI),
        "mean_G": np.mean(G)
    }