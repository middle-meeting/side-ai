FROM python:3.10-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev build-base

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
