# 📬 Webhook InLead + BotConversa API

Este projeto expõe uma API com FastAPI para receber formulários enviados pelo InLead e encaminhar mensagens personalizadas via WhatsApp usando a API do BotConversa.

---

## 🚀 Tecnologias

- Python 3.11
- FastAPI
- Docker + Docker Compose
- httpx (HTTP client async)
- BotConversa API (integração WhatsApp)

---

## ⚙️ Como rodar localmente com Docker

### 1. Clone o projeto

Instale o [docker desktop](https://www.youtube.com/watch?v=1gEFgYdmNZA)

### 2. Preencha o arquivo `.env` com seu token da BotConversa

```env
BOTCONVERSA_TOKEN=seu_token_real_aqui
```

### 3. Para rodar a aplicação utilize o comando

```bash
docker compose up --build
```

A API estará disponível em: [http://localhost:8000/webhook/inlead](http://localhost:8000/webhook/inlead)

---

## Endpoint

### `POST /webhook/inlead`

**Content-Type:** `multipart/form-data`

#### Parâmetros esperados:

| Campo        | Tipo   | Descrição                             |
|--------------|--------|-----------------------------------------|
| nome_tutor   | string | Nome do tutor (ex: "Carla")             |
| telefone     | string | Número de WhatsApp (ex: 35999998888)    |
| nome_cao     | string | Nome do cão (ex: "Thor")                |

#### Exemplo de requisição com `curl`:

```bash
curl -X POST http://localhost:8000/webhook/inlead \
  -F "nome_tutor=Carla" \
  -F "telefone=35999998888" \
  -F "nome_cao=Thor"
```
