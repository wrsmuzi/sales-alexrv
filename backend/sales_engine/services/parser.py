from playwright.sync_api import sync_playwright
from sales_engine.core.database import supabase
from sales_engine.core.logger import get_logger
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import urllib.parse

logger = get_logger("parser")

class GoogleMapsParser:
    def __init__(self):
        self.base_url = "https://www.google.com/maps/search/"

    def fetch_lead_details(self, lead_url, name, region, keyword):
        """Синхронна функція для збору даних одного ліда в окремому потоці"""
        try:
            with sync_playwright() as p:
                # Використовуємо headless=True для фонових потоків, щоб не відкривати 10 вікон
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                page.goto(lead_url, wait_until="domcontentloaded", timeout=20000)
                
                website = None
                try:
                    website_el = page.query_selector('//a[contains(@aria-label, "Website")]')
                    if website_el:
                        website = website_el.get_attribute('href')
                except: pass
                
                phone = "N/A"
                try:
                    phone_el = page.query_selector('//span[contains(@class, "phoneNumber")]')
                    if phone_el:
                        phone = phone_el.inner_text()
                except: pass
                
                browser.close()
                return {
                    "company_name": name,
                    "website": website if website else lead_url,
                    "phone": phone,
                    "region": region,
                    "category": keyword,
                    "status": "new",
                    "source": "google_maps",
                    "profile_url": lead_url
                }
        except Exception as e:
            logger.debug(f"Error fetching details for {name}: {e}")
            return None

    def search_leads(self, keyword: str, region: str):
        logger.info(f"🚀 Turbo Sync search started for {keyword} in {region}...")
        try:
            with sync_playwright() as p:
                # Головне вікно залишаємо видимим, щоб ти бачив прогрес і міг розгадати капчу
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                browser = p.chromium.launch(headless=False) 
                context = browser.new_context(user_agent=user_agent)
                page = context.new_page()
                
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                search_query = f"{keyword} in {region}"
                url = f"{self.base_url}{search_query.replace(' ', '+')}"
                logger.info(f"🔗 Navigating to: {url}")
                
                page.goto(url, wait_until="domcontentloaded")
                
                # БРОНЕБІЙНИЙ ПОШУК: пробуємо різні селектори
                selectors = [
                    '//div[contains(@class, "hfpxzc")]', 
                    '//a[contains(@href, "/maps/place/")]',
                    '//div[contains(@role, "feed")]//a'
                ]
                
                found_elements = []
                for selector in selectors:
                    try:
                        logger.info(f"Trying selector: {selector}")
                        page.wait_for_selector(selector, timeout=5000)
                        elements = page.query_selector_all(selector)
                        if elements:
                            found_elements = elements
                            logger.info(f"✅ Found {len(elements)} leads with selector {selector}")
                            break
                    except:
                        continue
                
                if not found_elements:
                    logger.warning("No results found with any known selectors.")
                    browser.close()
                    return []
                
                # ПОСИЛЕНИЙ СКРОЛІНГ для більшої кількості лідів
                try:
                    scrollable_div = page.locator('div[role="feed"]')
                    if scrollable_div.count() > 0:
                        logger.info("📜 Starting deep scroll to find more leads...")
                        for i in range(10): # Збільшили до 10 разів
                            scrollable_div.evaluate("el => el.scrollTop += 3000")
                            page.wait_for_timeout(random.randint(1500, 2500)) # Рандомні паузи для імітації людини
                            logger.debug(f"Scroll {i+1}/10 completed.")
                except Exception as e:
                    logger.warning(f"Scroll interrupted: {e}")
                
                # ЗБІР ВСІХ ЗНАЙШЕНИХ ПОСИЛАНЬ
                all_links = page.query_selector_all('//a[contains(@href, "/maps/place/")]')
                
                raw_leads = []
                logger.info(f"📦 Total elements found after scroll: {len(all_links)}. Parsing top 30...")
                
                for el in all_links[:30]:
                    try:
                        url = el.get_attribute('href')
                        if not url: continue
                        
                        # Намагаємось дістати ім'я з aria-label або тексту
                        aria_label = el.get_attribute('aria-label')
                        if aria_label:
                            name = aria_label.split(',')[0]
                        else:
                            name = el.inner_text().split('\n')[0] if el.inner_text() else "Unknown"
                        
                        raw_leads.append((name, url))
                    except: continue

                logger.info(f"📦 Found {len(raw_leads)} leads. Parallel deep-dive starting...")
                browser.close()

                # ПАРАЛЕЛЬНИЙ ЗБІР ДЕТАЛЕЙ через ThreadPoolExecutor (Windows-Safe)
                final_leads = []
                with ThreadPoolExecutor(max_workers=5) as executor:
                    # Створюємо список завдань
                    future_to_lead = {executor.submit(self.fetch_lead_details, url, name, region, keyword): name for name, url in raw_leads}
                    
                    for future in as_completed(future_to_lead):
                        result = future.result()
                        if result:
                            final_leads.append(result)

                if supabase and final_leads:
                    # Batch Insert
                    res = supabase.table('leads').insert(final_leads).execute()
                    if res.data:
                        logger.info(f"✅ Successfully saved {len(res.data)} leads to database.")
                        return res.data
                
                return final_leads
        except Exception as e:
            logger.exception(f"❌ Playwright Turbo Sync Error: {e}")
            return []

class SocialParser:
    def __init__(self):
        self.platforms = {
            "instagram": "instagram.com",
            "facebook": "facebook.com",
            "twitter": "twitter.com",
            "reddit": "reddit.com"
        }

    def search_social_profiles(self, keyword: str, region: str, platform: str):
        logger.info(f"🔍 Starting Social Search: {platform} | Keyword: {keyword} | Region: {region}")
        if platform not in self.platforms: 
            logger.error(f"❌ Platform {platform} is not supported.")
            return []

        domain = self.platforms[platform]
        search_query = f'site:{domain} {keyword} {region} -inurl:posts -inurl:reels -inurl:explore'
        url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        logger.info(f"🔗 Generated Search URL: {url}")
        
        try:
            with sync_playwright() as p:
                logger.info(f"🌐 Opening browser (VISIBLE MODE). If you see a CAPTCHA, please solve it!")
                browser = p.chromium.launch(headless=False) 
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, wait_until="networkidle")
                
                # ПОСИЛЕНИЙ ДЕТЕКТОР БЛОКУВАННЯ
                content = page.content().lower()
                page_title = page.title().lower()
                
                is_blocked = any(x in content for x in ["unusual traffic", "captcha", "robot", "verify you are not a robot"]) or \
                             any(x in page_title for x in ["captcha", "robot"])
                
                # Також вважаємо блокуванням, якщо знайдено дуже мало посилань (типово для сторінки капчі)
                initial_links = page.query_selector_all('a')
                if is_blocked or len(initial_links) < 10:
                    logger.warning("⚠️ GOOGLE BLOCK DETECTED! Browser is staying open. Please solve the CAPTCHA now.")
                    # Чекаємо 60 секунд, поки користувач розгадує капчу
                    page.wait_for_timeout(60000) 
                    logger.info("⏰ Time's up! Attempting to collect leads after CAPTCHA solve...")
                
                # Збираємо посилання (після можливого розгадування капчі)
                links = page.query_selector_all('a')
                logger.info(f"📦 Found {len(links)} total links on the page.")
                
                profiles = []
                for link in links:
                    href = link.get_attribute('href')
                    if not href: continue
                    
                    if domain in href and "/search" not in href and "google.com" not in href:
                        if "url?q=" in href:
                            href = href.split("url?q=")[1].split("&")[0]
                            href = urllib.parse.unquote(href)
                        
                        if any(seg in href for seg in ["/p/", "/reels/", "/stories/", "/explore/", "/tags/", "/posts/", "/about/"]):
                            continue
                            
                        profile_name = href.split('/')[-1] if href.endswith('/') == False else href.split('/')[-2]
                        if profile_name and profile_name not in ["explore", "about", "contact", "login", "signup", "home"]:
                            profiles.append({
                                "company_name": profile_name,
                                "website": href,
                                "region": region,
                                "category": keyword,
                                "status": "new",
                                "source": platform,
                                "profile_url": href
                            })
                
                browser.close()
                unique_profiles = list({p['website']: p for p in profiles}.values())
                logger.info(f"✅ Extracted {len(unique_profiles)} unique profiles from {platform}.")
                
                if supabase and unique_profiles:
                    logger.info(f"💾 Saving {len(unique_profiles)} social leads to database...")
                    res = supabase.table('leads').insert(unique_profiles).execute()
                    return res.data if res.data else unique_profiles
                
                return unique_profiles
        except Exception as e:
            logger.exception(f"❌ Social Parser Error: {e}")
            return []
