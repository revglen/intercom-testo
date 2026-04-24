
import logging
from dotenv import load_dotenv
import requests
from contextlib import asynccontextmanager
import httpx
from datetime import datetime, timezone

from config import config
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from routers.contact_router import router as contacts_router_process
from routers.conversations_router import router as conversations_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()

# ============================================================
# Help Functions
# ============================================================


app=FastAPI(
    title="Intercom Fin AI Agent Testo",
    description="Intercom Fin AI Agent Testo",
    version="1.0.0"
    #lifespan=lifespan
)

app.include_router(contacts_router_process)
app.include_router(conversations_router)

# ============================================================
# API Endpoints
# ============================================================
@app.get("/")
@app.post("/")
async def main_body():
    logger.info(f"You have reached Fin AI Agent Testo")
    return {"message": "You have reached Fin AI Agent Testo"}

@app.get("/health")
async def health_check():
    logger.info(f"Fin AI Agent Testo is up and running")
    return {"status": "healthy", "service": "Fin AI Agent Testo"}

# @app.post("/url-testo")
# @app.get("/url-testo")
# async def url_testo():
#     try:
#         url = config.INTERCOM_URL + "/fin/start"
#         timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

#         logger.info(f"The URL is {url} at {timestamp}")
#         print(f"The URL is {url} at {timestamp}")

#         data = {
#             "conversation_id": "ext-123",
#             "message": {
#                 "author": "user",
#                 "body": "How can I see my account details?",
#                 "timestamp": timestamp
#             },
#             "user": {
#                 "id": "123456",
#                 "name": "John Doe",
#                 "email": "john.doe@example.com"
#             }
#         }

#         response = requests.post(url, headers=getHeaders(), json=data)

#         return {
#             "status_code": response.status_code,
#             "response_text": response.text
#         }

#     except Exception as e:
#         logger.exception("start_fin failed")
#         raise HTTPException(status_code=500, detail=str(e))



# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fin_agent:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )