import os
import google.generativeai as genai
from sales_engine.core.database import supabase
from sales_engine.core.logger import get_logger
import json

logger = get_logger("ai_analyst")

class AIAnalyst:
    def __init__(self):
        logger.info("Initializing AIAnalyst...")
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY is missing from environment variables")
            raise ValueError("GEMINI_API_KEY is missing from environment variables")
        
        genai.configure(api_key=api_key)
        
        self.model = self._select_best_model()
        self.daily_limit = int(os.environ.get("DAILY_LEAD_LIMIT", "20"))
        
        self.mini_persona = """
        You are a Lead Qualifier for AlexRV-Dev. Your task is to quickly identify if a business is high-value.
        You must provide your analysis in two languages:
        1. Ukrainian (for internal team review)
        2. English (for client facing)
        
        Identify a key digital flaw and assign a score 1-10.
        Format:
        UA: [Ukrainian analysis]
        EN: [English analysis]
        SCORE: [1-10]
        """
        
        self.luxury_persona = """
        You are the Lead Strategist at AlexRV-Dev. You are a world-class luxury consultant.
        STATUS OVER SERVICE: Never offer 'services'. Offer 'transformation' and 'market dominance'.
        TONE: Confident, direct, sophisticated. No AI-cliches (avoid 'unlock', 'comprehensive', 'game-changer').
        
        You must generate the offer in two languages:
        1. Ukrainian (for internal review)
        2. English (for the client)
        
        Format:
        UA: [Ukrainian offer]
        EN: [English offer]
        """
        
        self.case_studies = [
            {"niche": "Real Estate", "result": "Increased lead flow by 300% for a Dubai Luxury Villa agency by implementing a high-status funnel.", "ua": "Збільшили потік лідів на 300% для агентства з розкішних вілл у Дубаї через впровадження статусної воронки."},
            {"niche": "Concierge/Lifestyle", "result": "Closed 5 UHNWI clients in 30 days for a London concierge service using hyper-personalized outreach.", "ua": "Закрили 5 клієнтів UHNWI за 30 днів для консьєрж-сервісу в Лондоні за допомогою гіпер-персоналізованого аутрічу."},
            {"niche": "Private Aviation/Yachts", "result": "Secured partnerships with 3 yacht charter firms in Monaco by highlighting digital exclusivity gaps.", "ua": "Забезпечили партнерство з 3 фірмами з чартеру яхт у Монако, підсвітивши прогалини в цифровій ексклюзивності."},
            {"niche": "Medical/Wellness", "result": "Increased high-ticket appointment bookings by 50% for a Swiss anti-aging clinic via authoritative content positioning.", "ua": "Збільшили кількість записів на високочекові процедури на 50% для швейцарської клініки омолодження через позиціонування авторитетного контенту."},
            {"niche": "Art/Jewelry", "result": "Scaled private collection sales for a New York gallery by targeting UHNWI through niche digital galleries.", "ua": "Масштабували продажі приватних колекцій для нью-йоркської галереї, таргетуючи UHNWI через нішеві цифрові галереї."},
            {"niche": "Financial/Wealth", "result": "Generated $2M in new AUM for a boutique wealth management firm in Singapore using a status-driven LinkedIn strategy.", "ua": "Залучили $2 млн нових активів під управління для бутикової фірми з управління капіталом у Сінгапурі за допомогою стратегії статусу в LinkedIn."},
            {"niche": "General Luxury", "result": "Transformed a boutique luxury brand's digital presence, leading to a 40% increase in average order value.", "ua": "Трансформували цифрову присутність бутикового люкс-бренду, що призвело до збільшення середнього чека на 40%."}
        ]

    def _select_best_model(self):
        """Force use of gemini-1.5-flash for high quota and stability."""
        logger.info("Scanning available Gemini models for maximum stability...")
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # ПРІОРИТЕТ №1: Gemini 1.5 Flash (найвищий ліміт)
            for model_name in available_models:
                if 'gemini-1.5-flash' in model_name:
                    logger.info(f"Selected stable-quota model: {model_name}")
                    return genai.GenerativeModel(model_name)
            
            # ПРІОРИТЕТ №2: Будь-яка інша доступна модель
            if available_models:
                logger.info(f"Flash not found. Using fallback: {available_models[0]}")
                return genai.GenerativeModel(available_models[0])
                
        except Exception as e:
            logger.error(f"Error listing models: {e}. Using default flash.")
        
        return genai.GenerativeModel('gemini-1.5-flash')

    def _get_best_case_study(self, lead_category: str):
        category = lead_category.lower()
        for study in self.case_studies:
            if study["niche"].lower() in category:
                return study
        return self.case_studies[-1]

    async def check_limit(self):
        try:
            res = supabase.table('analysis').select('*', count='exact').execute()
            if res.count >= self.daily_limit:
                logger.warning(f"Daily lead limit ({self.daily_limit}) reached.")
                return False
            return True
        except Exception as e:
            logger.error(f"Error checking daily limit: {e}")
            return True

    async def analyze_lead(self, lead_id: str):
        logger.info(f"Analyzing lead: {lead_id}...")
        if not await self.check_limit():
            return {"error": "Daily limit reached. Stop for today."}

        try:
            lead = supabase.table('leads').select('*').eq('id', lead_id).single().execute().data
            if not lead:
                return {"error": "Lead not found"}

            prompt = f"Analyze this business: {lead['company_name']} in {lead['region']}. Website: {lead['website']}. Category: {lead['category']}. Find one main digital flaw and assign a score 1-10."
            
            try:
                response = self.model.generate_content([self.mini_persona, prompt])
                analysis_text = response.text
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    logger.warning("Quota exceeded. Trying emergency fallback to Flash...")
                    try:
                        fallback = genai.GenerativeModel('gemini-1.5-flash')
                        response = fallback.generate_content([self.mini_persona, prompt])
                        analysis_text = response.text
                    except:
                        return {"error": "ШІ перевантажений. Спробуйте через 10-20 секунд."}
                else:
                    raise e
            
            score = 7
            if "SCORE:" in analysis_text:
                try:
                    score = int(analysis_text.split("SCORE:")[1].strip().split()[0])
                except: pass
            
            supabase.table('analysis').insert({
                "lead_id": lead_id,
                "lead_score": score,
                "business_analysis": analysis_text,
                "suggested_solution": "Initial analysis complete"
            }).execute()
            
            return {"score": score, "analysis": analysis_text}
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                return {"error": "ШІ перевантажений. Спробуйте пізніше."}
            logger.exception(f"❌ Gemini Analyze Error: {e}")
            return {"error": str(e)}

    async def create_offer(self, lead_id: str):
        logger.info(f"Generating offer for lead: {lead_id}...")
        try:
            lead = supabase.table('leads').select('*').eq('id', lead_id).single().execute().data
            analysis = supabase.table('analysis').select('*').eq('lead_id', lead_id).single().execute().data
            
            if not lead or not analysis:
                return {"error": "Missing lead or analysis data"}

            study = self._get_best_case_study(lead['category'])
            prompt = (
                f"Create a high-status, provocative outreach message for {lead['company_name']}. "
                f"Context: {analysis['business_analysis']}. "
                f"Case Study to include: {study['result']}. "
                f"Goal: Get a call. Max 3-4 sentences. Use a tone of exclusivity."
            )
            
            try:
                response = self.model.generate_content([self.luxury_persona, prompt])
                offer_text = response.text
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    logger.warning("Quota exceeded. Trying emergency fallback...")
                    try:
                        fallback = genai.GenerativeModel('gemini-1.5-flash')
                        response = fallback.generate_content([self.luxury_persona, prompt])
                        offer_text = response.text
                    except:
                        return {"error": "ШІ перевантажений. Спробуйте за кілька секунд."}
                else:
                    raise e

            offer_ua = ""
            offer_en = ""
            if "UA:" in offer_text and "EN:" in offer_text:
                try:
                    parts = offer_text.split("EN:")
                    offer_ua = parts[0].replace("UA:", "").strip()
                    offer_en = parts[1].strip()
                except:
                    offer_ua = offer_text
                    offer_en = offer_//text
            else:
                offer_ua = offer_text
                offer_en = offer_text
            
            offer_payload = json.dumps({"ua": offer_ua, "en": offer_en}, ensure_ascii=False)
            
            supabase.table('offers').insert({
                "lead_id": lead_id,
                "offer_text": offer_payload,
                "channel": "multi-channel"
            }).execute()
            
            return {"ua": offer_ua, "en": offer_en}
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                return {"error": "ШІ перевантажений. Спробуйте пізніше."}
            logger.exception(f"❌ Gemini Offer Error: {e}")
            return {"error": str(e)}
