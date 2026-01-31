import cv2
import numpy as np


def segment_leaf_hsv(
    img_rgb,
    lower_green=(25, 40, 40),
    upper_green=(85, 255, 255),
    kernel_size=5
):
    """
    Segment green regions using HSV thresholding.
    Returns a cleaned binary mask.
    """
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

    lower = np.array(lower_green, dtype=np.uint8)
    upper = np.array(upper_green, dtype=np.uint8)

    mask = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask


def extract_main_leaf_center_first(
    img_rgb,
    hsv_mask,
    crop_ratio=0.7
):
    """
    Extract main leaf by cropping center first,
    then selecting the largest contour inside the crop.
    """
    # 1. center crop image & mask
    cropped_img, (ox, oy) = center_crop(img_rgb, crop_ratio)
    cropped_mask, _ = center_crop(hsv_mask, crop_ratio)

    # 2. find contours in cropped mask
    contours, _ = cv2.findContours(
        cropped_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        raise ValueError("No contours found in center region")

    largest = max(contours, key=cv2.contourArea)

    # 3. create full-size mask
    full_mask = np.zeros(hsv_mask.shape, dtype=np.uint8)

    # shift contour back to original coordinates
    largest[:, 0, 0] += ox
    largest[:, 0, 1] += oy

    cv2.drawContours(full_mask, [largest], -1, 255, thickness=cv2.FILLED)

    return full_mask


def apply_mask(img_rgb, mask):
    """
    Apply binary mask to RGB image.
    """
    return cv2.bitwise_and(img_rgb, img_rgb, mask=mask)

def center_crop(img, crop_ratio=0.7):
    """
    Crop image around center with given ratio.
    crop_ratio=0.7 means keep 70% center area.
    """
    h, w = img.shape[:2]
    ch, cw = int(h * crop_ratio), int(w * crop_ratio)

    start_y = (h - ch) // 2
    start_x = (w - cw) // 2

    cropped = img[start_y:start_y+ch, start_x:start_x+cw]
    return cropped, (start_x, start_y)