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

    print("GLI min:", np.nanmin(GLI))
    print("GLI mean:", np.nanmean(GLI))
    print("GLI max:", np.nanmax(GLI))


    return {
        "mean_ExG": np.mean(ExG),
        "std_ExG": np.std(ExG),
        "mean_GLI": np.mean(GLI),
        "std_GLI": np.std(GLI),
        "mean_G": np.mean(G)
    }

def compute_gli_map(img_rgb, mask):
    """
    Generate Green Leaf Index (GLI) heatmap image.
    """
    img = img_rgb.astype(np.float32)

    R = img[:, :, 0]
    G = img[:, :, 1]
    B = img[:, :, 2]

    gli = (2 * G - R - B) / (2 * G + R + B + 1e-6)

    # background di-nol-kan
    gli[mask == 0] = np.nan

    # normalize GLI to 0–255
    gli_min = np.nanmin(gli)
    gli_max = np.nanmax(gli)

    gli_norm = (gli - gli_min) / (gli_max - gli_min + 1e-6)
    gli_norm = (gli_norm * 255).astype(np.uint8)

    # colormap (konsisten dengan ExG)
    gli_colormap = cv2.applyColorMap(gli_norm, cv2.COLORMAP_TURBO)

    return gli_colormap

def extract_exg_gli_values(img_rgb, mask):
    img = img_rgb.astype(float)

    R = img[:, :, 0]
    G = img[:, :, 1]
    B = img[:, :, 2]

    exg = 2 * G - R - B
    gli = (2 * G - R - B) / (2 * G + R + B + 1e-6)

    exg_vals = exg[mask > 0]
    gli_vals = gli[mask > 0]

    return exg_vals, gli_vals