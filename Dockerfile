FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
# CPU-only torch first, otherwise pip pulls multi-GB CUDA wheels.
# Long timeout, resume and a cache mount so a slow connection does not restart the torch download.
ENV PIP_DEFAULT_TIMEOUT=120 PIP_RESUME_RETRIES=10
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r requirements.txt
COPY . .
ENV PATHFINDER_DATA=/data
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
