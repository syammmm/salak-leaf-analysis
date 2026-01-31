# ---- Base image ----
FROM python:3.11-slim

# ---- Environment ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# ---- System dependencies (OpenCV needs these) ----
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /app

# ---- Install Python deps ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy app ----
COPY . .

# ---- Expose Cloud Run port ----
EXPOSE 8080

# ---- Run app ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]