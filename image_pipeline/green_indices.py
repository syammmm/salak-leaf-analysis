import numpy as np

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