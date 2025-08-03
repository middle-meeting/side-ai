from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import requests
import os
import re
from dotenv import load_dotenv
from prompt import build_prompt

# Load environment variables from .env
load_dotenv()

app = FastAPI()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME")

class Message(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class ChatRequest(BaseModel):
    personaName: str          # 이름
    personaAge: int           # 나이
    personaGender: str        # 성별
    personaSymptom: str       # 증상
    personaHistory: str       # 과거력(가족력)
    personaPersonality: str   # 성향성격
    personaDisease: str       # 병명
    messages: List[Message]

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    persona_dict = {
        "personaName": req.personaName,
        "personaAge": req.personaAge,
        "personaGender": req.personaGender,
        "personaSymptom": req.personaSymptom,
        "personaHistory": req.personaHistory,
        "personaPersonality": req.personaPersonality,
        "personaDisease": req.personaDisease,
    }
    prompt = build_prompt(persona_dict, [msg.dict() for msg in req.messages])
    payload = {
        "model": OLLAMA_MODEL_NAME,
        "messages": prompt,
        "stream": False,
        "options": {
            "temperature": 0.5,  # 더 일관된 응답을 위해 낮춤
            "top_p": 0.8,        # 더 예측 가능한 응답
            "repeat_penalty": 1.2, # 반복 방지 강화
            "num_ctx": 2048      # 컨텍스트 길이 제한
        }
    }

    try:
        # 1차: 환자 응답 생성 (최대 3회 재시도)
        raw_answer = None
        for attempt in range(3):
            try:
                response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                raw_answer = result["choices"][0]["message"]["content"].strip()
                
                # 1차 응답 기본 검증
                if len(raw_answer) > 5 and not raw_answer.startswith("AI 응답"):
                    break
                    
            except (requests.RequestException, KeyError) as e:
                if attempt == 2:  # 마지막 시도
                    raw_answer = "죄송합니다. 현재 응답을 생성할 수 없습니다."
                continue
        
        if not raw_answer:
            return ChatResponse(answer="서비스에 일시적인 문제가 있습니다.")
        
        final_answer = raw_answer
        
    except Exception as e:
        final_answer = "죄송합니다. 일시적인 오류가 발생했습니다."

    return ChatResponse(answer=final_answer)

