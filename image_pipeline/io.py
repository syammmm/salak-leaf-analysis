import cv2
import numpy as np

def load_image_from_bytes(image_bytes: bytes):
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Gambar tidak valid atau rusak.")

    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)