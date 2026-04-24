from logging import config

from fastapi import APIRouter, HTTPException
import httpx
import requests
from contact import ContactRequest, ContactResponse
from internal_headers import getHeaders
from config import config

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"],
)

# =========================================================
# ✅ 1. Create a new contact
# =========================================================
@router.post("/")
async def create_contact(contact_request: ContactRequest): 
    
    headers = getHeaders()
    url = f"{config.INTERCOM_URL}/contacts"

    #create contact
    contact_payload = {
        "role": contact_request.role,
        "external_id": contact_request.external_id,
        "email": contact_request.email,
        "name": contact_request.name
    }

    try:
        response = requests.post(url, headers=headers, json=contact_payload, timeout=30)
        response.raise_for_status()
   
        return map_contact(response.json())
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code

        # ✅ Handle 409 specifically for duplicates - already existing contacts
        if status_code == 409:
            return {
                "message": "Contact already exists",
                "status_code": 409
            }

        raise HTTPException(
            status_code=status_code,
            detail=e.response.text
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Request failed: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

# =========================================================
# ✅ 2. Get a contact via ID
# =========================================================
@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(contact_id: str):
    try:
        url = f"{config.INTERCOM_URL}/contacts/{contact_id}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=getHeaders())

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        return map_contact(response.json())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# ✅ 3. GET contact by email
# =========================================================
@router.get("/email/{email}", response_model=ContactResponse)
async def get_contact_by_email(email: str):
    try:
        url = f"{config.INTERCOM_URL}/contacts/search"

        payload = {
            "query": {
                "field": "email",
                "operator": "=",
                "value": email
            }
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=getHeaders(), json=payload)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        data = response.json()

        # Intercom returns list → pick first match
        contacts = data.get("data", [])

        if not contacts:
            raise HTTPException(status_code=404, detail="Contact not found")

        return map_contact(contacts[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def map_contact(data: dict) -> ContactResponse:
    return ContactResponse(
        type=data.get("type"),
        id=data.get("id"),
        workspace_id=data.get("workspace_id"),
        external_id=data.get("external_id"),
        role=data.get("role"),
        email=data.get("email"),
        phone=data.get("phone"),
        name=data.get("name"),
    )