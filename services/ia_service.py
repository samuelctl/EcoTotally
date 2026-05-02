from dotenv import load_dotenv
from google import genai
from fastapi import HTTPException
import json
import os
from datetime import date

GEMINI_REQUEST_LIMIT = int(os.getenv("GEMINI_REQUEST_LIMIT", "20"))
_gemini_usage = {"date": date.today().isoformat(), "count": 0}


def _verificar_limite_gemini():
    hoje = date.today().isoformat()
    if _gemini_usage["date"] != hoje:
        _gemini_usage["date"] = hoje
        _gemini_usage["count"] = 0

    if _gemini_usage["count"] >= GEMINI_REQUEST_LIMIT:
        raise HTTPException(
            status_code=429,
            detail={
                "codigo": "LIMITE_GEMINI_ATINGIDO",
                "mensagem": "O limite de 20 requisições da IA foi atingido por hoje. Tente novamente mais tarde.",
                "limite": GEMINI_REQUEST_LIMIT,
                "usadas": _gemini_usage["count"],
                "restantes": 0
            }
        )

    _gemini_usage["count"] += 1


def _traduzir_erro_gemini(e: Exception):
    texto = str(e).lower()
    if "429" in texto or "quota" in texto or "rate" in texto or "resource_exhausted" in texto:
        raise HTTPException(
            status_code=429,
            detail={
                "codigo": "LIMITE_GEMINI_ATINGIDO",
                "mensagem": "A IA atingiu o limite de uso no momento. Tente novamente mais tarde.",
                "limite": GEMINI_REQUEST_LIMIT,
                "usadas": _gemini_usage["count"],
                "restantes": max(GEMINI_REQUEST_LIMIT - _gemini_usage["count"], 0)
            }
        )
    raise HTTPException(status_code=500, detail=f"Erro na IA: {str(e)}")


load_dotenv()

_client = None


def get_gemini_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY não encontrada no ambiente"
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _parse_json_response(texto: str) -> dict:
    texto = texto.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="A IA respondeu em formato inválido"
        )


def gerar_recomendacao_ia(insights: dict):
    _verificar_limite_gemini()
    client = get_gemini_client()

    prompt = f"""
Você é um assistente financeiro inteligente.

Analise os dados abaixo e gere resposta em JSON puro.
Não use markdown.
Não invente dados.

Dados:
{json.dumps(insights, ensure_ascii=False)}

Formato obrigatório:
{{
  "diagnostico_geral": "texto",
  "alerta_amostra_regional": "texto",
  "nivel_urgencia": "baixo ou medio ou alto",
  "economia_estimativa_mensal": 0,
  "recomendacoes": [
    {{
      "titulo": "texto curto",
      "descricao": "texto prático",
      "categoria": "transporte, alimentacao, agua, energia, produtos ou outros",
      "impacto": "baixo ou medio ou alto"
    }}
  ]
}}

Regras:
- Responder em português
- Máximo 3 recomendações
- Se a amostra regional for pequena, avisar claramente
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return _parse_json_response(response.text)

    except HTTPException:
        raise

    except Exception as e:
        _traduzir_erro_gemini(e)


def _montar_historico(insights: dict, pergunta: str, historico: list) -> list:
    sistema = (
        "Você é um assistente financeiro inteligente dentro de um aplicativo.\n"
        "Responda em português do Brasil, de forma clara, objetiva e prática.\n"
        "Se a amostra regional for pequena, deixe isso claro na resposta.\n"
        "Se preciso use os dados abaixo"
        "Se o usuario tiver qualquer duvida responda ele com dados reais,nao invente,EX:o dia de hoje"
        "Não use markdown. Seja direto.\n\n"
        f"Dados do usuário:\n{json.dumps(insights, ensure_ascii=False)}"
    )

    mensagens = [
        {"role": "user", "parts": [{"text": sistema}]},
        {"role": "model", "parts": [{"text": "Entendido. Pode perguntar."}]},
    ]

    for msg in historico:
        role = "user" if msg["role"] == "user" else "model"
        mensagens.append({"role": role, "parts": [{"text": msg["content"]}]})

    mensagens.append({"role": "user", "parts": [{"text": pergunta}]})

    return mensagens


def gerar_resposta_chat_ia(insights: dict, pergunta: str, historico: list = []) -> str:
    _verificar_limite_gemini()
    client = get_gemini_client()
    mensagens = _montar_historico(insights, pergunta, historico)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=mensagens
        )
        return response.text.strip()

    except HTTPException:
        raise

    except Exception as e:
        _traduzir_erro_gemini(e)