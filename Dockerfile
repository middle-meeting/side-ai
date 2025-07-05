FROM python:3.10-alpine

WORKDIR /app

# 빌드에 필요한 패키지 설치
RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt .

# pip, setuptools 최신화
RUN pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
