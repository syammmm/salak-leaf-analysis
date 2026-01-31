# 🌿 Salak Leaf Analysis

Aplikasi web berbasis FastAPI untuk analisis kesehatan daun salak menggunakan pemrosesan gambar dan indeks vegetasi hijau.

## 📋 Daftar Isi

- [Fitur](#fitur)
- [Tech Stack](#tech-stack)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Instalasi](#instalasi)
- [Cara Menjalankan](#cara-menjalankan)
- [Alur Kerja (Upload hingga Hasil)](#alur-kerja-upload-hingga-hasil)
- [Struktur Direktori](#struktur-direktori)
- [API Endpoints](#api-endpoints)

---

## 🎯 Fitur

- **Upload Gambar Daun**: Mendukung format JPG/PNG dengan maksimal 5 MB
- **Analisis Visual**: Segmentasi daun dan perhitungan indeks vegetasi
- **Penilaian Kesehatan**: Skor visual berdasarkan indeks ExG dan GLI
- **Visualisasi Hasil**: Menampilkan gambar segmentasi daun yang diproses
- **Penyimpanan Otomatis**: Hasil disimpan di `temp/uploads/` dengan ID unik
- **Pembersihan Otomatis**: Background task untuk menghapus upload lama

---

## 🛠️ Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Frontend**: HTML + Tailwind CSS
- **Image Processing**: OpenCV + NumPy
- **Template Engine**: Jinja2

---

## 💻 Persyaratan Sistem

- Python 3.8+
- pip atau conda
- macOS / Linux / Windows

---

## 🚀 Instalasi

### 1. Clone atau Download Project
```bash
cd /path/to/Salak-IoT
```

### 2. Buat Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
# atau
venv\Scripts\activate          # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Dependencies:
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `python-multipart` - File upload support
- `jinja2` - HTML template engine
- `opencv-python` - Image processing
- `numpy` - Numerical computing

---

## ⚙️ Cara Menjalankan

### Development Mode
```bash
# Dari root directory project
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Akses Aplikasi
Buka browser dan akses:
```
http://localhost:8000
```

---

## 📸 Alur Kerja (Upload hingga Hasil)

### Flow Diagram
```
User Upload Gambar
       ↓
   ✓ Validasi Format & Ukuran
       ↓
   Generate UUID untuk Session ID
       ↓
   Load Gambar ke Memory
       ↓
   ┌─ Preprocessing
   ├─ Segmentasi HSV → Deteksi Daun Hijau
   ├─ Extract Main Leaf → Daun Terbesar
   └─ Apply Mask → Isolasi Daun
       ↓
   Hitung Indeks Vegetasi (ExG & GLI)
       ↓
   Hitung Visual Score (0-100)
       ↓
   ┌─ Simpan Gambar Segmentasi
   ├─ Path: temp/uploads/{UUID}/leaf_segmented.png
   └─ Simpan Metadata JSON
       ↓
   Tampilkan Hasil ke Frontend
```

### Tahap Per Tahap

#### 1. **Upload Gambar**
```
POST /upload
- Input: File gambar (JPG/PNG, max 5MB)
- Validasi: Format, ukuran, readability
```

**Contoh Request:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "image=@path/to/daun.jpg"
```

#### 2. **Validasi Gambar**
Dalam `app/routers/leaf.py` - fungsi `validate_image()`:
- ✓ Format: `image/jpeg`, `image/png`
- ✓ Ukuran: ≤ 5 MB
- ✓ Readability: OpenCV dapat membaca file

#### 3. **Preprocessing & Segmentasi**
Dalam `image_pipeline/pipeline.py`:
```python
# a) Load dari memory
img_rgb = load_image_from_bytes(image_bytes)

# b) Preprocessing (resize, normalisasi)
img_prep = preprocess_image(img_rgb)

# c) Segmentasi HSV
mask_green = segment_leaf_hsv(img_prep)

# d) Extract daun terbesar
mask_leaf = extract_main_leaf_center_first(img_prep, mask_green)

# e) Aplikasi mask
leaf_only = apply_mask(img_prep, mask_leaf)
```

#### 4. **Perhitungan Indeks Vegetasi**
Dalam `image_pipeline/green_indices.py`:
- **ExG** (Excess Green): $ExG = 2G - R - B$ (sensitivitas hijau tinggi)
- **GLI** (Green Leaf Index): $GLI = \frac{2G - R - B}{2G + R + B}$ (-1 hingga 1)

#### 5. **Penilaian Kesehatan**
Dalam `image_pipeline/scoring.py`:
```
Score = f(mean_ExG, mean_GLI)
0-100 → Label: Sehat / Kurang Sehat / Tidak Sehat
```

#### 6. **Penyimpanan Hasil**
Struktur penyimpanan:
```
temp/uploads/
└── {UUID}/
    ├── leaf_segmented.png          # Gambar hasil segmentasi
    └── (metadata dalam response)   # JSON hasil analisis
```

**Contoh UUID**: `9181c0b7-dc2c-4502-8522-9f3c4da54f9b`

#### 7. **Tampilan Hasil**
Frontend menampilkan:
- **Skor Visual**: 0-100
- **ExG Index**: Nilai rata-rata
- **GLI Index**: Nilai rata-rata  
- **Status**: Label kesehatan daun
- **Gambar Segmentasi**: Preview dari `temp/uploads/{UUID}/leaf_segmented.png`

---

## 📁 Struktur Direktori

```
Salak-IoT/
├── app/
│   ├── config.py               # Konfigurasi aplikasi
│   ├── logger.py               # Setup logging
│   ├── main.py                 # Entry point FastAPI
│   ├── routers/
│   │   └── leaf.py             # Route untuk upload & analisis
│   ├── static/
│   │   └── style.css           # Styling Tailwind CSS
│   ├── templates/
│   │   └── index.html          # Frontend form & hasil
│   └── utils/
│       └── cleanup.py          # Pembersihan upload lama
│
├── image_pipeline/             # Pipeline pemrosesan gambar
│   ├── __init__.py
│   ├── pipeline.py             # Orkestrasi pipeline
│   ├── io.py                   # Load gambar dari bytes
│   ├── preprocessing.py        # Resize, normalisasi
│   ├── segmentation.py         # Deteksi & segmentasi daun
│   ├── green_indices.py        # Hitung ExG & GLI
│   └── scoring.py              # Hitung visual score
│
├── temp/
│   └── uploads/                # 📁 Penyimpanan hasil upload
│       └── {UUID}/
│           └── leaf_segmented.png
│
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
└── README.md                   # Dokumentasi ini
```

---

## 🔌 API Endpoints

### GET `/`
Menampilkan halaman utama (form upload).

**Response**: HTML page

---

### POST `/upload`
Endpoint untuk upload dan proses gambar daun.

**Request:**
```
Content-Type: multipart/form-data
Parameter: image (file)
```

**Response (Success - 200):**
```json
{
  "result": {
    "score": 78,
    "label": "Sehat",
    "exg": 45.23,
    "gli": 0.142,
    "image_url": "/temp/uploads/9181c0b7-dc2c-4502-8522-9f3c4da54f9b/leaf_segmented.png"
  },
  "filename": "daun.jpg"
}
```

**Response (Validation Error - 400):**
```json
{
  "error_message": "Format file tidak didukung. Gunakan JPG atau PNG."
}
```

**Response (Processing Error - 500):**
```json
{
  "error_message": "Terjadi kesalahan saat memproses gambar. Pastikan foto daun jelas dan pencahayaan cukup."
}
```

---

## 📝 Logging

Aplikasi menggunakan Python logging dengan configuration di `app/logger.py`.

Level log:
- **INFO**: Proses normal (upload, processing complete)
- **WARNING**: Validasi gagal, segmentasi kosong
- **ERROR**: Exception tidak tertangani

Cek logs dengan:
```bash
# Live logs
tail -f app.log

# atau dari stdout saat running uvicorn
```

---

## 🧹 Background Tasks

### Cleanup Otomatis
Setiap upload, background task menjalankan `cleanup_old_uploads()` untuk:
- Menghapus folder upload yang lebih tua dari N hari (configurable)
- Membersihkan temp directory

Lihat: `app/utils/cleanup.py`

---

## 🐳 Docker (Optional)

Build dan run dengan Docker:
```bash
# Build image
docker build -t salak-iot .

# Run container
docker run -p 8000:8000 -v $(pwd)/temp:/app/temp salak-iot
```

---

## 🐛 Troubleshooting

### Error: "Segmentasi gagal: empty mask"
- **Penyebab**: Daun tidak terdeteksi atau background sama dengan warna daun
- **Solusi**: Ambil foto dengan kontras lebih jelas, pencahayaan lebih terang

### Error: "Format file tidak didukung"
- **Penyebab**: File bukan JPG atau PNG
- **Solusi**: Gunakan format JPG atau PNG

### Error: "Ukuran file terlalu besar"
- **Penyebab**: Gambar > 5 MB
- **Solusi**: Kompres gambar atau gunakan resolusi lebih rendah

### Upload folder terus membesar
- **Penyebab**: Cleanup task tidak berjalan
- **Solusi**: Cek background tasks di `app/utils/cleanup.py`, verifikasi permissions

---

## 📚 Referensi

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenCV Documentation](https://opencv.org/)
- [Excess Green Index (ExG)](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index)
- [Green Leaf Index (GLI)](https://www.indexdatabase.de/)

---

## 📄 Lisensi

Project ini dibuat untuk keperluan analisis kesehatan daun salak.

---

## 📧 Support

Untuk pertanyaan atau issue, silakan buat issue di repository ini.

---

**Last Updated**: January 31, 2026
