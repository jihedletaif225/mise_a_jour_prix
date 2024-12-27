


import logging
import streamlit as st
from playwright.async_api import async_playwright
import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductDeactivator:
    """Handles the logic and automation tasks for deactivating products."""

    def __init__(self, username, password):
        self.username = username
        self.password = password

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
                logger.info("Verifying successful login...")
                await page.wait_for_selector('td[align="center"][style="background-color:#eeeeee"]:has-text("© Copyright 2024 - Restoconcept")', timeout=5000)
                logger.info("Login successful.")
                return True
            except Exception:
                logger.error("Login failed: Footer not found.")
                return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    async def perform_search_and_uncheck(self, page, reference) -> bool:
        """Searches for a product by reference and unchecks the active checkbox."""
        try:
            logger.info(f"Navigating to search page for reference: {reference}...")
            await page.goto("https://www.restoconcept.com/admin/SA_prod.asp")
            await page.fill('input[name="showPhrase"]', reference)
            await page.click('button:has-text("Rechercher")')


            await page.click('tr td a:has-text("Editer")')

            checkbox_selector = 'img[alt="Décocher tout"]'
            await page.wait_for_selector(checkbox_selector, timeout=5000)

            logger.info("Unchecking the checkbox...")
            await page.click(checkbox_selector)

            logger.info("Submitting changes...")
            await page.click('form[name="prodForm"] button:has-text("Mettre à jour")')
            logger.info(f"Successfully processed reference: {reference}")
            return True
        except Exception as e:
            logger.error(f"Error processing reference {reference}: {e}")
            return False

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


class ProductDeactivationApp:
    """Manages the Streamlit UI for the product deactivation tool."""

    def __init__(self):
        self.username = None
        self.password = None
        self.references = []
        self.headless = True

    def run(self):
        """Launches the Streamlit interface."""
        st.title("Product Deactivation Tool")

        # Input fields
        self.username = st.text_input("Username", value="")
        self.password = st.text_input("Password", value="", type="password")
        references_text = st.text_area("Product References (one per line)")
        self.references = [ref.strip() for ref in references_text.splitlines() if ref.strip()]
        self.headless = st.checkbox("Run in headless mode?", value=True)

        # Start automation button
        if st.button("Start Deactivation"):
            if self.username and self.password and self.references:
                st.info("Starting deactivation process...")
                self.start_automation()
            else:
                st.warning("Please fill out all required fields.")

    def start_automation(self):
        """Initiates the deactivation process."""
        with st.spinner("Running automation..."):
            try:
                deactivator = ProductDeactivator(self.username, self.password)
                asyncio.run(deactivator.run_automation(self.references, self.headless))
                st.success("Deactivation completed successfully.")
            except Exception as e:
                st.error(f"An error occurred: {e}")


# Run the Streamlit app
if __name__ == "__main__":
    app = ProductDeactivationApp()
    app.run()
