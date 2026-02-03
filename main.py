from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import hashlib
import time

app = FastAPI(title="Innovia360 AEJ Engine")

# --- SÉCURITÉ ---
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME)
VALID_KEYS = {"SLIM_ADMIN_2026", "CLIENT_TEST_001"} # À stocker en BDD plus tard

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key in VALID_KEYS: return api_key
    raise HTTPException(status_code=403, detail="Clé API Invalide")

# --- MODÈLE DE DONNÉES ---
class AEJRequest(BaseModel):
    agent_id: str
    tokens: int
    compute_time: float

# --- MOTEUR DE CALCUL ---
@app.post("/certify")
async def certify(data: AEJRequest, api_key: str = Depends(get_api_key)):
    # Formule AEJ : (Efficience relative)
    effort = (data.tokens * 0.01) + (data.compute_time * 0.5)
    score = min(round((data.tokens / (effort + 0.1)) * 5, 2), 100.0)
    
    # Signature cryptographique pour protéger le résultat
    sig_str = f"{data.agent_id}-{score}-INNOVIA_SECRET"
    signature = hashlib.sha256(sig_str.encode()).hexdigest()

    return {
        "status": "SUCCESS",
        "aej_score": score,
        "energy_joules": round(effort, 2),
        "signature": signature,
        "verify_url": f"https://aejoules.com/v/{data.agent_id}"
    }