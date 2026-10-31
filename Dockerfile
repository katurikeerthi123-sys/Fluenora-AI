FROM python:3.11-slim

WORKDIR /app

# Install minimal system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies with CPU-optimized PyTorch
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy full application (including pre-built React frontend & trained models)
COPY . .

EXPOSE 8000
ENV PORT=8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
