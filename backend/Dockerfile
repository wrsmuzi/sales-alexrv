
FROM python:3.12-slim
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libexpat1 \
    libX11-6 \
    libXcomposite1 \
    libXdamage1 \
    libXext6 \
    libXfixes3 \
    libXrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium --with-deps
COPY . .
EXPOSE 8080
CMD ["uvicorn", "sales_engine.main:app", "--host", "0.0.0.0", "--port", "8080"]
