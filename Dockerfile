FROM python:3.10-slim 

WORKDIR /app

# 시스템 패키지 설치 (Debian 기반)
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel cython

RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
