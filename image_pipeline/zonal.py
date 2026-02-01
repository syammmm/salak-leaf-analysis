import numpy as np


def create_geometric_zones(mask_leaf,
                           center_thresh=0.35,
                           ring_thresh=0.65):
    """
    Create geometric zonal masks (center, ring, edge)
    from leaf mask.

    Parameters
    ----------
    mask_leaf : np.ndarray
        Binary mask of leaf (H, W), >0 = leaf
    center_thresh : float
        Relative distance threshold for center zone
    ring_thresh : float
        Relative distance threshold for ring zone

    Returns
    -------
    mask_center, mask_ring, mask_edge : np.ndarray
        Binary masks for each zone
    """

    # pastikan mask boolean
    leaf_pixels = mask_leaf > 0

    # ambil koordinat pixel daun
    coords = np.column_stack(np.where(leaf_pixels))

    if coords.shape[0] == 0:
        raise ValueError("Mask daun kosong, tidak bisa membuat zona.")

    # centroid (y, x)
    centroid_y, centroid_x = coords.mean(axis=0)

    # hitung jarak tiap pixel ke centroid
    distances = np.sqrt(
        (coords[:, 0] - centroid_y) ** 2 +
        (coords[:, 1] - centroid_x) ** 2
    )

    # normalisasi jarak
    max_dist = distances.max()
    norm_dist = distances / (max_dist + 1e-6)

    # siapkan mask kosong
    mask_center = np.zeros_like(mask_leaf, dtype=np.uint8)
    mask_ring = np.zeros_like(mask_leaf, dtype=np.uint8)
    mask_edge = np.zeros_like(mask_leaf, dtype=np.uint8)

    # klasifikasi zona
    for (y, x), d in zip(coords, norm_dist):
        if d <= center_thresh:
            mask_center[y, x] = 255
        elif d <= ring_thresh:
            mask_ring[y, x] = 255
        else:
            mask_edge[y, x] = 255

    # print("Leaf pixels :", np.sum(mask_leaf > 0))
    # print("Center pixels:", np.sum(mask_center > 0))
    # print("Ring pixels  :", np.sum(mask_ring > 0))
    # print("Edge pixels  :", np.sum(mask_edge > 0))
    return mask_center, mask_ring, mask_edge
