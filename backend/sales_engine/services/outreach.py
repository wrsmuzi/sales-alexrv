import os
import resend
from sales_engine.core.database import supabase
from sales_engine.core.logger import get_logger
import json

logger = get_logger("outreach")

class OutreachManager:
    def __init__(self):
        logger.info("Initializing OutreachManager...")
        # Встановлюємо API ключ безпосередньо в модуль resend
        resend.api_key = os.environ.get("RESEND_API_KEY")
        if not resend.api_key:
            logger.error("RESEND_API_KEY is missing from environment variables")

    async def send_offer(self, offer_id: str):
        logger.info(f"Attempting to send offer {offer_id}...")
        try:
            # 1. Get offer and lead data
            offer_res = supabase.table('offers').select('*, leads(*)').eq('id', offer_id).single().execute()
            offer = offer_res.data
            
            if not offer:
                logger.error(f"Offer {offer_id} not found in database.")
                return {"status": "error", "message": "Offer not found"}
            
            lead = offer['leads']
            if not lead or not lead.get('email'):
                logger.warning(f"No email address found for lead linked to offer {offer_id}")
                return {"status": "error", "message": "No email address found for this lead"}

            # Parse the offer text to use the English version
            try:
                offer_data = json.loads(offer['offer_text'])
                email_body = offer_data.get('en') or offer_data.get('ua') or offer['offer_text']
            except:
                email_body = offer['offer_text']

            # 2. Send via Resend using the Emails module
            logger.info(f"Sending email to {lead['email']} for {lead['company_name']}...")
            data = resend.Emails.send({
                "from": "AlexRV-Dev <onboarding@resend.dev>",
                "to": [lead['email']],
                "subject": f"Exclusive Strategic Proposal for {lead['company_name']}",
                "html": f"<strong>Personalized Proposal</strong><br><br>{email_body}"
            })
            
            # 3. Update status in DB
            supabase.table('offers').update({"is_sent": True, "sent_at": "now()"}).eq('id', offer_id).execute()
            
            logger.info(f"Successfully sent email to {lead['email']}. Resend ID: {data['id']}")
            return {"status": "success", "id": data['id']}
        except Exception as e:
            logger.exception(f"❌ Outreach Error for offer {offer_id}: {e}")
            return {"status": "error", "message": str(e)}
