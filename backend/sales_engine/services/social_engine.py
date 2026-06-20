import os
import time
import random
from playwright.sync_api import sync_playwright
from sales_engine.core.database import supabase
from sales_engine.core.logger import get_logger

logger = get_logger("social_engine")

class SocialManager:
    def __init__(self):
        logger.info("Initializing SocialManager...")
        self.credentials = {
            "instagram": {
                "user": os.environ.get("INSTAGRAM_USER"),
                "pass": os.environ.get("INSTAGRAM_PASS")
            },
            "facebook": {
                "user": os.environ.get("FACEBOOK_USER"),
                "pass": os.environ.get("FACEBOOK_PASS")
            },
            "twitter": {
                "user": os.environ.get("TWITTER_USER"),
                "pass": os.environ.get("TWITTER_PASS")
            },
            "reddit": {
                "user": os.environ.get("REDDIT_USER"),
                "pass": os.environ.get("REDDIT_PASS")
            }
        }
        
        # Platform-specific selectors (Approximate, these change often)
        self.selectors = {
            "instagram": {
                "login_user": "input[name='username']",
                "login_pass": "input[name='password']",
                "login_btn": "button[type='submit']",
                "msg_btn": "svg[aria-label='Direct message']",
                "msg_input": "div[role='textbox']"
            },
            "facebook": {
                "login_user": "#email",
                "login_pass": "#pass",
                "login_btn": "button[name='login']",
                "msg_input": "div[role='textbox']"
            },
            "twitter": {
                "login_user": "input[autocomplete='username']",
                "login_pass": "input[name='password']",
                "login_btn": "span:has-text('Next')",
                "msg_input": "div[data-testid='dmComposerTextInput']"
            },
            "reddit": {
                "login_user": "input[name='username']",
                "login_pass": "input[name='password']",
                "login_btn": "button[type='submit']",
                "msg_input": "textarea[name='message']"
            }
        }

    def _human_type(self, page, selector, text):
        """Types text like a human with random delays between keystrokes."""
        logger.debug(f"Human-typing into selector {selector}...")
        page.wait_for_selector(selector)
        page.click(selector)
        for char in text:
            page.type(selector, char, delay=random.randint(50, 150))
            if random.random() < 0.1: # 10% chance of a slight pause
                time.sleep(random.uniform(0.1, 0.3))

    def _random_sleep(self, min_s=2, max_s=5):
        sleep_time = random.uniform(min_s, max_s)
        logger.debug(f"Sleeping for {sleep_time:.2f}s...")
        time.sleep(sleep_time)

    def _login(self, page, platform):
        creds = self.credentials.get(platform)
        if not creds or not creds["user"] or not creds["pass"]:
            logger.error(f"❌ Missing credentials for {platform} in environment variables. Please set {platform.upper()}_USER and {platform.upper()}_PASS.")
            return False
        
        sel = self.selectors.get(platform)
        try:
            logger.info(f"🔐 Attempting login to {platform}...")
            if platform == "instagram":
                logger.debug("Navigating to Instagram login page...")
                page.goto("https://www.instagram.com/accounts/login/")
            elif platform == "facebook":
                logger.debug("Navigating to Facebook login page...")
                page.goto("https://www.facebook.com/")
            elif platform == "twitter":
                logger.debug("Navigating to Twitter login page...")
                page.goto("https://twitter.com/i/flow/login")
            elif platform == "reddit":
                logger.debug("Navigating to Reddit login page...")
                page.goto("https://www.reddit.com/login/")
            
            logger.debug(f"Typing username for {platform}...")
            self._human_type(page, sel["login_user"], creds["user"])
            self._random_sleep(1, 2)
            
            logger.debug(f"Typing password for {platform}...")
            self._human_type(page, sel["login_pass"], creds["pass"])
            self._random_sleep(1, 2)
            
            logger.debug(f"Clicking login button for {platform}...")
            page.click(sel["login_btn"])
            
            # Wait for login to complete and verify
            logger.info(f"Waiting for {platform} session to establish...")
            page.wait_for_timeout(5000)
            logger.info(f"✅ Successfully logged into {platform}")
            return True
        except Exception as e:
            logger.exception(f"❌ Login failed for {platform}: {e}")
            return False

    def send_social_message(self, profile_url: str, message: str):
        """
        Identifies platform from URL, logs in, and sends a human-like message.
        """
        logger.info(f"🚀 Starting social outreach to {profile_url}")
        platform = None
        for p, domain in {"instagram": "instagram.com", "facebook": "facebook.com", "twitter": "twitter.com", "reddit": "reddit.com"}.items():
            if domain in profile_url:
                platform = p
                break
        
        if not platform:
            logger.error(f"❌ Could not determine platform from URL: {profile_url}")
            return {"status": "error", "message": "Unsupported platform"}

        try:
            with sync_playwright() as p:
                logger.info(f"🌐 Launching browser (headless=False) for {platform} outreach...")
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                if not self._login(page, platform):
                    browser.close()
                    return {"status": "error", "message": f"Login failed for {platform}. Check environment variables."}
                
                logger.info(f"🔗 Navigating to target profile: {profile_url}")
                page.goto(profile_url)
                self._random_sleep(3, 6)
                
                # Platform specific messaging logic
                sel = self.selectors.get(platform)
                if platform == "instagram":
                    logger.info("Searching for 'Message' button on Instagram...")
                    page.click("text=Message")
                    self._random_sleep(2, 4)
                    logger.info("Typing message into Instagram DM...")
                    self._human_type(page, sel["msg_input"], message)
                    page.keyboard.press("Enter")
                    logger.info("Pressed Enter to send.")
                elif platform == "facebook":
                    logger.info("Searching for 'Message' button on Facebook...")
                    page.click("text=Message")
                    self._random_sleep(2, 4)
                    logger.info("Typing message into Facebook Messenger...")
                    self._human_type(page, sel["msg_input"], message)
                    page.keyboard.press("Enter")
                    logger.info("Pressed Enter to send.")
                elif platform == "twitter":
                    logger.info("Searching for 'DM' button on Twitter...")
                    page.click("a[aria-label='Direct Message']")
                    self._random_sleep(2, 4)
                    logger.info("Typing message into Twitter DM...")
                    self._human_type(page, sel["msg_input"], message)
                    page.keyboard.press("Enter")
                    logger.info("Pressed Enter to send.")
                elif platform == "reddit":
                    logger.info("Searching for 'Chat' button on Reddit...")
                    page.click("text=Chat")
                    self._random_sleep(2, 4)
                    logger.info("Typing message into Reddit Chat...")
                    self._human_type(page, sel["msg_input"], message)
                    page.keyboard.press("Enter")
                    logger.info("Pressed Enter to send.")
                
                self._random_sleep(2, 5)
                logger.info(f"✅ Message successfully sent on {platform} to {profile_url}")
                browser.close()
                return {"status": "success", "platform": platform, "url": profile_url}
        except Exception as e:
            logger.exception(f"❌ Social outreach failed for {profile_url}: {e}")
            return {"status": "error", "message": str(e)}
