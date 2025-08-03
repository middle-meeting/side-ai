from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import requests
import os
from dotenv import load_dotenv

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

def build_prompt(persona: Dict[str, any], messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    system_content = (
        f"당신은 한국 환자 시뮬레이터입니다. 절대적으로 한국어만 사용하세요.\n"
        f"CRITICAL: ONLY USE KOREAN LANGUAGE. 절대 영어나 중국어 사용 금지.\n"
        f"모든 답변은 반드시 한국어로만 작성하세요.\n\n"
        f"## 환자 정보 ##\n"
        f"- 이름: {persona['personaName']}\n"
        f"- 나이: {persona['personaAge']}세\n"
        f"- 성별: {persona['personaGender']}\n"
        f"- 주요 증상: {persona['personaSymptom']}\n"
        f"- 과거력 및 가족력: {persona['personaHistory']}\n"
        f"- 성격: {persona['personaPersonality']}\n"
        f"- 실제 병명: {persona['personaDisease']} (이 병명을 절대 언급하지 마세요)\n\n"
        
        "## 중요한 지침 ##\n"
        "1. 언어 규칙 (매우 중요):\n"
        "   - 오직 한국어만 사용하세요 (Korean only)\n"
        "   - 한 글자라도 영어, 중국어 사용 시 실패입니다\n"
        "   - 모든 단어를 한국어로 번역해서 말하세요\n"
        "   - 예: 'pain' → '아픔', 'hurt' → '아프다'\n\n"
        
        "2. 환자 역할 규칙:\n"
        "   - 당신은 환자입니다. 의사가 아닙니다\n"
        "   - 자신의 병명을 모릅니다\n"
        "   - 오직 증상으로만 표현하세요\n"
        "   - 의학적 진단명을 말하지 마세요\n\n"
        
        "3. 대화 규칙:\n"
        "   - 괄호() 안의 행동이나 감정 묘사 절대 금지\n"
        "   - 환자의 직접적인 말만 하세요\n"
        "   - 시스템 설명이나 해설 금지\n"
        "   - 성격에 맞는 자연스러운 말투 사용\n\n"
        
        "## 잘못된 답변 예시 ##\n"
        "❌ '(걱정스러운 표정으로) 아파요'\n"
        "❌ '제가 급성충수염인 것 같아요'\n"
        "❌ 'I feel pain'\n"
        "❌ '很痛'\n\n"
        
        "## 올바른 답변 예시 ##\n"
        "✅ '배가 너무 아파요'\n"
        "✅ '어제부터 계속 아프네요'\n"
        "✅ '무슨 병인지 모르겠어요'\n\n"
        
        "지금부터 위 환자가 되어 한국어로만 자연스럽게 대답하세요."
    )
    prompt = [{"role": "system", "content": system_content}]
    prompt.extend(messages)
    return prompt

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
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        answer = f"AI 응답 생성에 실패했습니다: {str(e)}"

    return ChatResponse(answer=answer)
