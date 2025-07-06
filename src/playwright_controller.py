"""
Playwright controller for page navigation and element interactions
"""
from typing import Optional, Dict, Any, List
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from loguru import logger
from config import settings


class PlaywrightController:
    """Controller for Playwright browser automation"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    def start_browser(self) -> None:
        """Start browser and create context"""
        try:
            self.playwright = sync_playwright().start()
            
            # Choose browser type
            if settings.browser_type == "firefox":
                self.browser = self.playwright.firefox.launch(headless=settings.headless)
            elif settings.browser_type == "webkit":
                self.browser = self.playwright.webkit.launch(headless=settings.headless)
            else:
                self.browser = self.playwright.chromium.launch(headless=settings.headless)
            
            # Create context
            self.context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            # Create page
            self.page = self.context.new_page()
            self.page.set_default_timeout(settings.timeout)
            
            logger.info(f"Browser started: {settings.browser_type}")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    def close_browser(self) -> None:
        """Close browser and cleanup"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            logger.info("Browser closed")
            
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    def navigate_to(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            if not self.page:
                self.start_browser()
            
            self.page.goto(url)
            self.page.wait_for_load_state("networkidle")
            
            logger.info(f"Navigated to: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def get_page_html(self) -> str:
        """Get current page HTML content"""
        try:
            if not self.page:
                raise Exception("Browser not started")
            
            html = self.page.content()
            logger.debug(f"Retrieved HTML content ({len(html)} chars)")
            return html
            
        except Exception as e:
            logger.error(f"Failed to get page HTML: {e}")
            return ""
    
    def get_page_url(self) -> str:
        """Get current page URL"""
        try:
            if not self.page:
                return ""
            return self.page.url
        except Exception as e:
            logger.error(f"Failed to get page URL: {e}")
            return ""
    
    def find_element(self, selector: str, selector_type: str = "xpath") -> bool:
        """Check if element exists on page"""
        try:
            if not self.page:
                return False
            
            if selector_type == "xpath":
                element = self.page.locator(f"xpath={selector}")
            else:
                element = self.page.locator(selector)
            
            return element.count() > 0
            
        except Exception as e:
            logger.error(f"Error finding element with selector {selector}: {e}")
            return False
    
    def click_element(self, selector: str, selector_type: str = "xpath") -> bool:
        """Click element by selector"""
        try:
            if not self.page:
                return False
            
            if selector_type == "xpath":
                element = self.page.locator(f"xpath={selector}")
            else:
                element = self.page.locator(selector)
            
            element.click()
            logger.info(f"Clicked element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            return False
    
    def type_text(self, selector: str, text: str, selector_type: str = "xpath") -> bool:
        """Type text into element"""
        try:
            if not self.page:
                return False
            
            if selector_type == "xpath":
                element = self.page.locator(f"xpath={selector}")
            else:
                element = self.page.locator(selector)
            
            element.fill(text)
            logger.info(f"Typed text into element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text into element {selector}: {e}")
            return False
    
    def select_option(self, selector: str, option_text: str, selector_type: str = "xpath") -> bool:
        """Select option from dropdown"""
        try:
            if not self.page:
                return False
            
            if selector_type == "xpath":
                element = self.page.locator(f"xpath={selector}")
            else:
                element = self.page.locator(selector)
            
            element.select_option(label=option_text)
            logger.info(f"Selected option '{option_text}' from: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to select option from {selector}: {e}")
            return False
    
    def get_element_text(self, selector: str, selector_type: str = "xpath") -> str:
        """Get text content of element"""
        try:
            if not self.page:
                return ""
            
            if selector_type == "xpath":
                element = self.page.locator(f"xpath={selector}")
            else:
                element = self.page.locator(selector)
            
            text = element.inner_text()
            logger.debug(f"Got text from element {selector}: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Failed to get text from element {selector}: {e}")
            return ""
    
    def wait_for_element(self, selector: str, selector_type: str = "xpath", timeout: int = None) -> bool:
        """Wait for element to appear"""
        try:
            if not self.page:
                return False
            
            timeout = timeout or settings.timeout
            
            if selector_type == "xpath":
                element = self.page.locator(f"xpath={selector}")
            else:
                element = self.page.locator(selector)
            
            element.wait_for(state="visible", timeout=timeout)
            logger.info(f"Element appeared: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Timeout waiting for element {selector}: {e}")
            return False
    
    def scroll_to_element(self, selector: str, selector_type: str = "xpath") -> bool:
        """Scroll to element"""
        try:
            if not self.page:
                return False
            
            if selector_type == "xpath":
                element = self.page.locator(f"xpath={selector}")
            else:
                element = self.page.locator(selector)
            
            element.scroll_into_view_if_needed()
            logger.info(f"Scrolled to element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll to element {selector}: {e}")
            return False
    
    def take_screenshot(self, path: str = "screenshot.png") -> bool:
        """Take screenshot of current page"""
        try:
            if not self.page:
                return False
            
            self.page.screenshot(path=path)
            logger.info(f"Screenshot saved: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
    
    def get_page_title(self) -> str:
        """Get page title"""
        try:
            if not self.page:
                return ""
            return self.page.title()
        except Exception as e:
            logger.error(f"Failed to get page title: {e}")
            return ""