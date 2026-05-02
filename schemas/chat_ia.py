from pydantic import BaseModel

class ChatIARequest(BaseModel):
    pergunta: str
    historico: list[dict] = []  # [{"role": "user/assistant", "content": "..."}]