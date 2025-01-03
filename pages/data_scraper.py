


import logging
import streamlit as st
from playwright.async_api import async_playwright
import asyncio
import platform
import pandas as pd

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Constants for readability and maintainability
LOGIN_PAGE_URL = "https://www.restoconcept.com/admin/logon.asp"
ADMIN_DEFAULT_URL = "https://www.restoconcept.com/admin/default.asp"
FOOTER_SELECTOR = (
    'td[align="center"][style="background-color:#eeeeee"]:has-text("© Copyright 2025 - Restoconcept")'
)

class RestauConceptScraper:
    """Handles the scraping logic for RestauConcept."""
    def __init__(self, username: str, password: str, marque: str):
        self.username = username
        self.password = password
        self.marque = marque

    async def login(self, page) -> bool:
        """Logs into the Restoconcept admin portal."""
        try:
            logger.info("Navigating to login page...")
            await page.goto("https://www.restoconcept.com/admin/logon.asp")
            await page.fill("#adminuser", self.username)
            await page.fill("#adminPass", self.password)
            await page.click("#btn1")

            # Check for successful login
            try:
                page.wait_for_selector(FOOTER_SELECTOR, timeout=5000)
                return True
            except Exception:
                if page.url == ADMIN_DEFAULT_URL:
                    logger.info("Login successful: Redirect to admin default page detected.")
                    return True
                else:
                    logger.error("Login failed: Neither footer nor admin default page detected.")
                    return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    async  def scrape_marque(self):  
        """Searches for a product by reference and unchecks the active checkbox."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            if await self.login(page):
                try:
                    await page.goto("https://www.restoconcept.com/admin/SA_prod.asp", wait_until="networkidle")
                    await page.select_option('select[name="marque"]', self.marque)
                    await page.click('button:has-text("Rechercher")')
                    await page.wait_for_load_state("networkidle")
                    edit_links = []
                    while True:
                        rows = await page.query_selector_all('table.listTable tr')
                        for row in rows:
                            tds = await row.query_selector_all("td")
                            if len(tds) >= 5:
                                first_td = await tds[0].inner_text()
                                second_td = await tds[1].inner_text()
                                eighth_td = await tds[7].inner_text()
                                edit_links.append({
                                    "Référence": second_td,
                                    "No": first_td,
                                    "Prix public": eighth_td,
                                })
                        next_links = await page.locator('a:has-text("Suiv.")').all()
                        if not next_links:
                            break
                        await next_links[0].click()
                        await page.wait_for_load_state("networkidle")
                    await browser.close()
                    return edit_links
                except Exception as e:
                    logger.error(f"Error during scraping: {e}")
                    await browser.close()
                    return None
            else:
                await browser.close()
                return None

    async def run_automation(self, references, headless=True):
        """Runs the automation process for multiple references."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            page = await browser.new_page()

            # Perform login
            if not await self.login(page):
                logger.error("Login failed. Aborting automation.")
                await browser.close()
                return False

            # Process references
            for reference in references:
                logger.info(f"Processing reference: {reference}")
                success = await self.perform_search_and_uncheck(page, reference)
                if not success:
                    logger.error(f"Failed to process reference: {reference}")

            await browser.close()
            return True


class ScraperApp:
    """Streamlit app for RestauConcept data scraper."""

    def __init__(self):
        self.username = None
        self.password = None
        self.marque = None
        self.scraper = None

    def run(self):
        """Run the Streamlit app."""
        st.title("RestauConcept Data Scraper")
        st.sidebar.header("User Login")
        self.username = st.sidebar.text_input("Username")
        self.password = st.sidebar.text_input("Password", type="password")
        self.marque = st.sidebar.text_input("Supplier/Brand (Marque)").strip()
        if st.sidebar.button("Start Scraping"):
            self.start_scraping()
        st.sidebar.markdown("""
        ---
        **Instructions:**
        1. Enter your username and password.
        2. Input the supplier/brand (marque).
        3. Click "Start Scraping" to fetch the data.
        """)
    def start_scraping(self):
        """Start the scraping process."""
        if not self.username or not self.password or not self.marque:
            st.error("Please fill out all fields.")
            return
        with st.spinner("Scraping data, please wait..."):

            try:
                # Initialize scraper and start scraping
                self.scraper = RestauConceptScraper(self.username, self.password, self.marque)
                links = asyncio.run(self.scraper.scrape_marque())
                if links:
                    st.success(f"Found {len(links)} products for marque {self.marque}.")
                    df = pd.DataFrame(links)
                    st.write(df)
                    # Export to Excel
                    output_file = f"{self.marque}_products.xlsx"
                    df.to_excel(output_file, index=False)
                    with open(output_file, "rb") as file:
                        st.download_button("Download Excel File", file, file_name=output_file)
                else:
                    st.warning("No products found or login failed.")

            except Exception as e:
                st.error(f"An error occurred: {e}")


# Run the Streamlit app
if __name__ == "__main__":
    app = ScraperApp()
    app.run()
