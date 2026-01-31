import cv2

def preprocess_image(img_rgb, size=(512, 512)):
    img_resized = cv2.resize(img_rgb, size)
    img_blur = cv2.GaussianBlur(img_resized, (5, 5), 0)
    return img_blur
