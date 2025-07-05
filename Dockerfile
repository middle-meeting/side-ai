FROM python:3.10-alpine

WORKDIR /app

# 필수 빌드 도구 설치
RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev build-base

# 사전 설치
COPY requirements.txt .

# pip 업그레이드 및 필수 툴 설치
RUN pip install --upgrade pip setuptools wheel cython

# PyYAML 빌드 에러 회피: --prefer-binary 사용
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# 앱 복사
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
