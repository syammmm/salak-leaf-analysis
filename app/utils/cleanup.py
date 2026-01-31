from pathlib import Path
from datetime import datetime
import shutil

from app.config import UPLOAD_DIR, UPLOAD_TTL


def cleanup_old_uploads():
    """
    Remove upload folders older than UPLOAD_TTL
    """
    base_dir = Path(UPLOAD_DIR)
    if not base_dir.exists():
        return

    now = datetime.now()

    for folder in base_dir.iterdir():
        if not folder.is_dir():
            continue

        try:
            # ambil waktu terakhir modifikasi
            mtime = datetime.fromtimestamp(folder.stat().st_mtime)

            if now - mtime > UPLOAD_TTL:
                shutil.rmtree(folder, ignore_errors=True)
                print(f"[CLEANUP] Removed {folder.name}")

        except Exception as e:
            print(f"[CLEANUP ERROR] {folder}: {e}")