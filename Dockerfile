FROM python:3.11-slim

WORKDIR /app

# CPU-only torch first — avoids pulling the 2GB CUDA build
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download trained models from GitHub if not already present (e.g. on HF Spaces)
RUN for asset in btc eth sol; do \
      if [ ! -f "models/ppo_${asset}_final.zip" ]; then \
        curl -fL "https://github.com/HussianRaza/cryptobot-rl/raw/master/models/ppo_${asset}_final.zip" \
             -o "models/ppo_${asset}_final.zip" && \
        echo "Downloaded ppo_${asset}_final.zip"; \
      fi; \
    done

# HF Spaces requires port 7860
EXPOSE 7860

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
