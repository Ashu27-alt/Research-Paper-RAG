FROM python:3.11-slim
# -------------------------
# 1. Set working directory
# -------------------------
WORKDIR /app
# -------------------------
# 2. Install system dependencies
# -------------------------
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/
# -------------------------
# 3. Install Python dependencies
# -------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# -------------------------
# 4. Copy application
# -------------------------
COPY app ./app
# -------------------------
# 5. Create upload directory
# -------------------------
RUN mkdir -p uploads
# -------------------------
# 6. Copy Alembic configuration
# -------------------------
COPY alembic.ini .
COPY alembic ./alembic
# -------------------------
# 7. Copy startup script
# -------------------------
COPY app/start.sh ./start.sh
RUN chmod +x ./start.sh
# -------------------------
# 8. Start application
# -------------------------
CMD ["./start.sh"]