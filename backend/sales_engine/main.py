import asyncio
import sys
import json
import os
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from sales_engine.core.database import supabase
from sales_engine.core.logger import get_logger
from sales_engine.services.parser import GoogleMapsParser, SocialParser
from sales_engine.services.ai_analyst import AIAnalyst
from sales_engine.services.outreach import OutreachManager
from sales_engine.services.social_engine import SocialManager

logger = get_logger("main")
app = FastAPI(title="AlexRV-Dev AI Sales Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=3)

class SearchQuery(BaseModel):
    keyword: str
    region: str

class SocialSearchQuery(BaseModel):
    keyword: str
    region: str
    platform: str

@app.get("/")
async def root():
    return {"status": "online"}

@app.get("/logs")
async def get_logs():
    log_path = "logs/sales_engine.log"
    try:
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return {"logs": [line.strip() for line in lines[-20:]]}
        return {"logs": []}
    except Exception as e:
        return {"error": str(e)}

@app.post("/search")
async def start_search(query: SearchQuery):
    loop = asyncio.get_event_loop()
    try:
        leads = await loop.run_in_executor(executor, lambda: GoogleMapsParser().search_leads(query.keyword, query.region))
        return {"status": "success", "leads_found": len(leads), "data": leads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-social")
async def start_social_search(query: SocialSearchQuery):
    loop = asyncio.get_event_loop()
    try:
        leads = await loop.run_in_executor(executor, lambda: SocialParser().search_social_profiles(query.keyword, query.region, query.platform))
        return {"status": "success", "leads_found": len(leads), "data": leads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.api_route("/analyze/{lead_id}", methods=["GET", "POST"])
async def analyze_lead(lead_id: str):
    try:
        analyst = AIAnalyst()
        result = await analyst.analyze_lead(lead_id)
        if "error" in result: raise HTTPException(status_code=400, detail=result['error'])
        return {"status": "success", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.api_route("/generate-offer/{lead_id}", methods=["GET", "POST"])
async def generate_offer(lead_id: str):
    try:
        analyst = AIAnalyst()
        offer = await analyst.create_offer(lead_id)
        if "error" in offer: raise HTTPException(status_code=400, detail=offer['error'])
        return {"status": "success", "offer": offer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send/{lead_id}")
async def send_offer(lead_id: str):
    try:
        offer_res = supabase.table('offers').select('*').eq('lead_id', lead_id).order('created_at', { 'ascending': False }).limit(1).execute()
        if not offer_res.data:
            raise HTTPException(status_code=404, detail="Оффер не знайдено")
        
        offer_id = offer_res.data[0]['id']
        manager = OutreachManager()
        result = await manager.send_offer(offer_id)
        if result.get("status") == "error": raise HTTPException(status_code=400, detail=result['message'])
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-social/{lead_id}")
async def send_social_offer(lead_id: str):
    loop = asyncio.get_event_loop()
    try:
        offer_res = supabase.table('offers').select('*').eq('lead_id', lead_id).order('created_at', { 'ascending': False }).limit(1).execute()
        if not offer_res.data:
            raise HTTPException(status_code=404, detail="Оффер не знайдено")
        
        offer_data = offer_res.data[0]
        lead_res = supabase.table('leads').select('*').eq('id', lead_id).single().execute()
        lead_data = lead_res.data
        
        try:
            offer_json = json.loads(offer_data['offer_text'])
            message = offer_json.get('en') or offer_json.get('ua') or offer_data['offer_text']
        except:
            message = offer_data['offer_text']
        
        result = await loop.run_in_executor(executor, lambda: SocialManager().send_social_message(lead_data['profile_url'], message))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str):
    try:
        supabase.table('leads').delete().eq('id', lead_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-leads")
async def clear_leads():
    try:
        supabase.table('offers').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('analysis').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('leads').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
