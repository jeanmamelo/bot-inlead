import logging
import os
import time

import httpx
from fastapi import FastAPI, Form, status
from fastapi.responses import JSONResponse

BOTCONVERSA_BASE_URL = "https://backend.botconversa.com.br/api/v1/webhook"
BOTCONVERSA_TOKEN = os.getenv("BOTCONVERSA_TOKEN")

app = FastAPI()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def dividir_nome(nome_tutor: str, nome_cao: str) -> tuple[str, str]:
    partes = nome_tutor.strip().split()
    return partes[0], " ".join(partes[1:]) if len(partes) > 1 else nome_cao


def criar_mensagem(nome_tutor: str, nome_cao: str) -> str:
    return f"Olá, falo com {nome_tutor}, responsável por {nome_cao}?"


async def verificar_ou_criar_subscriber(
    client: httpx.AsyncClient, telefone: str, nome_tutor: str, nome_cao: str, headers: dict
) -> int | None:
    get_url = f"{BOTCONVERSA_BASE_URL}/subscriber/get_by_phone/{telefone}/"
    response = await client.get(get_url, headers=headers)

    if response.status_code == 200:
        logger.info(f"Cliente encontrado no BotConversa, id={response.json().get('id')}.")
        return response.json().get("id")

    logger.info(f"{telefone} não cadastrado. Tentando cadastrar...")
    nome, sobrenome = dividir_nome(nome_tutor, nome_cao)
    payload = {"phone": telefone, "first_name": nome, "last_name": sobrenome}

    response = await client.post(f"{BOTCONVERSA_BASE_URL}/subscriber/", json=payload, headers=headers)
    if response.status_code != 200:
        logger.error(f"Erro ao cadastrar {telefone}: {response.text}")
        return None

    logger.info(f"{telefone} cadastrado com sucesso.")
    return response.json().get("id")


async def enviar_mensagem(client: httpx.AsyncClient, subscriber_id: int, mensagem: str, headers: dict) -> bool:
    url = f"{BOTCONVERSA_BASE_URL}/subscriber/{subscriber_id}/send_message/"
    payload = {"type": "text", "value": mensagem}
    time.sleep(180)  # Aguardar 3 minutos antes de enviar a mensagem
    response = await client.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        logger.info("Iniciando processamento de webhook InLead")
        return True

    logger.error(f"Erro ao enviar mensagem: {response.text}")
    return False


@app.post("/webhook/inlead")
async def receive_inlead_form(nome_tutor: str = Form(...), telefone: str = Form(...), nome_cao: str = Form(...)):
    logger.info("Iniciando processamento de webhook InLead")
    logger.info(f"Nome do tutor: {nome_tutor}, Telefone: {telefone}, Nome do cão: {nome_cao}")

    telefone = (
        telefone if telefone.startswith("55") or telefone.startswith("351") or telefone.startswith("1") else "55" + telefone
    )
    mensagem = criar_mensagem(nome_tutor, nome_cao)
    headers = {"Api-Key": BOTCONVERSA_TOKEN, "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        subscriber_id = await verificar_ou_criar_subscriber(client, telefone, nome_tutor, nome_cao, headers)
        if not subscriber_id:
            logger.error(f"Erro ao cadastrar {telefone}")
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={"detail": "Erro ao cadastrar telefone no BotConversa"},
            )

        sucesso = await enviar_mensagem(client, subscriber_id, mensagem, headers)
        if not sucesso:
            logger.error(f"Erro ao enviar mensagem para {telefone}")
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={"detail": "Erro ao enviar mensagem para BotConversa"},
            )

    logger.info(f"Mensagem enviada com sucesso para {telefone}")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Mensagem enviada com sucesso"})
