import numpy as np


def compute_index_stats(values):
    """
    Compute basic statistics for index values.
    """
    values = values[~np.isnan(values)]

    if values.size == 0:
        return {
            "mean": None,
            "std": None,
            "min": None,
            "max": None,
            "n_pixel": 0
        }

    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "n_pixel": int(values.size)
    }


def zonal_stats_exg_gli(
    img_rgb,
    mask_center,
    mask_ring,
    mask_edge
):
    """
    Compute ExG & GLI statistics for each zone.
    """
    img = img_rgb.astype(float)

    R = img[:, :, 0]
    G = img[:, :, 1]
    B = img[:, :, 2]

    exg = 2 * G - R - B
    gli = (2 * G - R - B) / (2 * G + R + B + 1e-6)

    zones = {
        "center": mask_center > 0,
        "ring": mask_ring > 0,
        "edge": mask_edge > 0
    }

    results = {}

    for zone_name, zone_mask in zones.items():
        exg_vals = exg[zone_mask]
        gli_vals = gli[zone_mask]

        results[zone_name] = {
            "ExG": compute_index_stats(exg_vals),
            "GLI": compute_index_stats(gli_vals)
        }

    return results