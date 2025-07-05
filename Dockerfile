# 베이스 이미지: python 3.10-alpine (가볍고 빠름)
FROM python:3.10-alpine

# 작업 디렉토리 생성 및 이동
WORKDIR /app

# 필요한 패키지 복사
COPY requirements.txt .

# 의존성 설치 (빌드 시점)
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 환경 변수 파일 복사 (선택 사항, 실제로는 .env는 CI에서 비공개 처리 권장)
# COPY .env .

# FastAPI 서버 실행 (uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
