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
        f"너는 가상의 인물 역할을 맡았다.\n"
        f"이 인물의 정보는 다음과 같다:\n"
        f"- 이름: {persona['personaName']}\n"
        f"- 나이: {persona['personaAge']}세\n"
        f"- 성별: {persona['personaGender']}\n"
        f"- 주요 증상: {persona['personaSymptom']}\n"
        f"- 과거력 및 가족력: {persona['personaHistory']}\n"
        f"- 성격: {persona['personaPersonality']}\n"
        f"- 병명: {persona['personaDisease']}\n\n"
        "너는 이 인물의 페르소나를 유지하며, "
        "질문에 대해 자연스럽고 사실적인 말투로 답변해야 한다. "
        "설정한 페르소나 정보를 바탕으로 자연스럽고 현실적인 말투로 대답하라. "
        "너는 해당 병명에 대해서는 절대적으로 모르고 그에 대한 증상으로 대답해라. "
        "단, 답변에서 괄호 () 안에 들어간 모든 묘사, 행동, 감정 표현은 절대 무조건 포함하지 마라. "
        "너는 절대 답변에 괄호 () 안의 모든 묘사, 행동, 감정 표현을 포함해서는 안 된다. "
        "절대로 괄호 안 내용을 답변에 넣지 말고, 오직 환자의 말만 자연스럽고 사실적으로 대답해야 한다. "
        "시스템 안내, 해설, 내레이션 같은 내용도 절대 포함하지 마라. "
        "꼭 기억해라. 괄호 안 내용은 절대 포함하지 마라. "
        "항상 환자의 말만, 환자의 입장에서만 대답하라. \n\n"
        "다음은 절대 하지 말아야 할 답변 예시다:\n"
        "(눈물을 글썽이며) 아파요.\n"
        "이렇게 답하라:\n"
        "아파요."
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
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        answer = f"AI 응답 생성에 실패했습니다: {str(e)}"

    return ChatResponse(answer=answer)
