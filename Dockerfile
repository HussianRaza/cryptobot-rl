FROM python:3.11-slim

WORKDIR /app

# CPU-only torch first — avoids pulling the 2GB CUDA build
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download trained models from GitHub if not already present (e.g. on HF Spaces)
RUN python - <<'EOF'
import urllib.request, os
base = "https://github.com/HussianRaza/cryptobot-rl/raw/master/models"
os.makedirs("models", exist_ok=True)
for asset in ["btc", "eth", "sol"]:
    path = f"models/ppo_{asset}_final.zip"
    if not os.path.exists(path):
        print(f"Downloading {path}...")
        urllib.request.urlretrieve(f"{base}/ppo_{asset}_final.zip", path)
        print(f"Done: {path}")
EOF

# HF Spaces requires port 7860
EXPOSE 7860

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
