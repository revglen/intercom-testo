import json
import logging
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
import httpx
from conversation import *
from internal_headers import getHeaders
from config import config

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# =========================================================
# ✅ 1. Start a Conversation
# =========================================================
@router.post("/", response_model=ConversationResponse)
async def start_conversation(request: RequestConversation):
    url = f"{config.INTERCOM_URL}/conversations"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=getHeaders(),
                json=request.to_intercom()
            )

            response.raise_for_status()
            data = response.json()

            #return data

            return ConversationResponse(
                type=data.get("type"),
                id=data.get("id") or data.get("conversation_id"),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
            )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    

# =========================================================
# ✅ 2. Search a Conversation
# =========================================================
@router.post("/search/{created_at}")
async def start_conversation(created_at: int):
    url = f"{config.INTERCOM_URL}/conversations/search"

    search_data={
        "query": {
            "operator": "AND",
            "value": [
            {
                "field": "created_at",
                "operator": ">",
                "value": "1776970000"
            }
            ]
        },
        "pagination": {
            "per_page": 5
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=getHeaders(),
                json=search_data
            )

            response.raise_for_status()
            data = response.json()

            return data

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )

# =========================================================
# ✅ 3. Reply to a Conversation
# =========================================================
@router.post("/{conversation_id}/reply")
async def reply_conversation(
    conversation_id: str,
    request: ReplyConversationRequest
):
    url = f"{config.INTERCOM_URL}/conversations/{conversation_id}/reply"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=getHeaders(),
                json=request.dict()
            )

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    
# =========================================================
# ✅ 4. Webhook
# =========================================================
@router.head("/webhook")
async def intercom_webhook_head():
    return Response(status_code=200)

@router.post("/webhook")
async def intercom_webhook(request: Request):
    try:
        raw_body = await request.body()

        if not raw_body:
            return JSONResponse(
                status_code=200,
                content={"message": "Webhook received with empty body"}
            )

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload: {raw_body!r}")
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid JSON payload"}
            )

        logger.info(f"Webhook received: {payload}")

        return JSONResponse(
            status_code=200,
            content={"message": "Webhook received successfully"}
        )

    except Exception as e:
        logger.exception("Webhook processing failed")
        return JSONResponse(
            status_code=500,
            content={"message": f"Unexpected error: {str(e)}"}
        )