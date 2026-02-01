from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import BackgroundTasks
import shutil
import uuid
from pathlib import Path
from image_pipeline.pipeline import process_leaf_image
from app.utils.cleanup import cleanup_old_uploads
import cv2
import numpy as np
import logging
logger = logging.getLogger("leaf-api")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = Path("temp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_image(upload: UploadFile, content: bytes):
    if upload.content_type not in ALLOWED_TYPES:
        raise ValueError("Format file tidak didukung. Gunakan JPG atau PNG.")

    if len(content) > MAX_FILE_SIZE:
        raise ValueError("Ukuran file terlalu besar. Maksimal 5 MB.")

    # cek apakah benar-benar image (OpenCV)
    img_array = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("File tidak dapat dibaca sebagai gambar.")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.post("/upload", response_class=HTMLResponse)
async def upload_leaf(
    request: Request,
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...)
):
    background_tasks.add_task(cleanup_old_uploads)

    try:
        logger.info(
            "Upload received | filename=%s | content_type=%s",
            image.filename, image.content_type
        )
        # READ ONCE
        content = await image.read()
        validate_image(image, content)

        # prepare output dir (per sample)
        sample_id = str(uuid.uuid4())
        sample_dir = UPLOAD_DIR / sample_id

        # PROCESS (IN-MEMORY)
        result = process_leaf_image(
            image_bytes=content,
            output_dir=str(sample_dir)
        )

        logger.info(
            "Processing success | score=%s | label=%s",
            result["score"], result["label"]
        )

        # build image url if exists
        if "segmented_image" in result:
            result["segmented_url"] = f"/temp/uploads/{sample_id}/{result['segmented_image']}"
        if "exg_image" in result:
            result["exg_url"] = f"/temp/uploads/{sample_id}/{result['exg_image']}"
        if "gli_image" in result:
            result["gli_url"] = f"/temp/uploads/{sample_id}/{result['gli_image']}"
        if "hist_exg" in result:
            result["hist_exg_url"] = f"/temp/uploads/{sample_id}/{result['hist_exg']}"
        if "hist_gli" in result:
            result["hist_gli_url"] = f"/temp/uploads/{sample_id}/{result['hist_gli']}"
        if "exg_overlay" in result: 
            result["exg_overlay_url"] = f"/temp/uploads/{sample_id}/{result['exg_overlay']}"
        if "gli_overlay" in result:
            result["gli_overlay_url"] = f"/temp/uploads/{sample_id}/{result['gli_overlay']}"

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": result,
                "filename": image.filename
            }
        )

    except ValueError as e:
        logger.warning("Validation error: %s", str(e))
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error_message": str(e)},
            status_code=400
        )

    except Exception as e:
        logger.exception("Unhandled error during image processing")
        print("[ERROR]", e)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error_message": (
                    "Terjadi kesalahan saat memproses gambar. "
                    "Pastikan foto daun jelas dan pencahayaan cukup."
                )
            },
            status_code=500
        )