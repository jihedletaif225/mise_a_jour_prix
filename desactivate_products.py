


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

class RestoconceptAutomation:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    async def login(self, page) -> bool:
        try:
            logger.info("Navigating to login page...")
            await page.goto("https://www.restoconcept.com/admin/logon.asp")
            await page.fill("#adminuser", self.username)
            await page.fill("#adminPass", self.password)
            await page.click("#btn1")

            try:
                logger.info("Waiting for the page to load after login...")
                await page.wait_for_selector('td[align="center"][style="background-color:#eeeeee"]:has-text("© Copyright 2024 - Restoconcept")', timeout=5000)
                logger.info("Login successful.")
                return True
            except:
                logger.error("Login failed: Copyright footer not found.")
                return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    async def perform_search_and_uncheck(self, page, reference) -> bool:
        try:
            logger.info(f"Navigating to the search page for reference {reference}...")
            await page.goto("https://www.restoconcept.com/admin/marges.asp")

            logger.info(f"Entering reference number: {reference}...")
            reference_input_selector = 'input[name="rch_phrase"]'
            await page.fill(reference_input_selector, reference)

            logger.info("Clicking the search button...")
            search_button_selector = 'button[type="submit"]'
            await page.click(search_button_selector)

            logger.info("Waiting for checkbox to appear...")
            checkbox_selector = 'td[style="padding:4px; border:1px #666 solid; text-align:center;"] input[type="checkbox"][name="active"]'

            try:
                await page.wait_for_selector(checkbox_selector, timeout=5000)
                logger.info("Checkbox is visible.")
                checkbox = await page.query_selector(checkbox_selector)
                await checkbox.uncheck()

                actualiser_button_selector = 'td[style="padding:4px; border:1px #666 solid; text-align:center;"] input[type="submit"][value="Actualiser"]'
                await page.click(actualiser_button_selector)

                logger.info(f"Checkbox unchecked and 'Actualiser' button clicked successfully for reference {reference}.")
                return True
            except Exception as e:
                logger.error(f"Error while interacting with checkbox for reference {reference}: {e}")
                return False
        except Exception as e:
            logger.error(f"Error during search and uncheck for reference {reference}: {e}")
            return False

async def main(username, password, references, headless):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)  # Use the headless parameter here
        page = await browser.new_page()

        automation = RestoconceptAutomation(username, password)

        logged_in = await automation.login(page)
        if logged_in:
            logger.info("Login successful.")
            for reference in references:
                logger.info(f"Processing reference: {reference}")
                result = await automation.perform_search_and_uncheck(page, reference)
                if result:
                    logger.info(f"Task completed successfully for reference {reference}.")
                else:
                    logger.error(f"Failed to complete the task for reference {reference}.")
        else:
            logger.error("Login failed.")

        await browser.close()

# Streamlit interface
def run_streamlit():
    st.title("Restoconcept Automation")

    # User inputs with Streamlit interface
    username = st.text_input("Username", value="")
    password = st.text_input("Password", value="", type="password")
    references = st.text_area("Product References (one per line)", "").splitlines()

    # Checkbox for headless mode
    headless = st.checkbox("Run in headless mode?", value=True)

    # Handle button click
    if st.button("Start Automation"):
        if username and password and references:
            # Display a progress bar for the task
            progress = st.progress(0)
            status_text = st.empty()

            try:
                # Start automation and provide progress updates
                for idx, reference in enumerate(references, 1):
                    status_text.text(f"Processing reference {reference} ({idx}/{len(references)})...")
                    asyncio.run(main(username, password, [reference], headless))
                    progress.progress(int((idx / len(references)) * 100))
                st.success("Automation completed successfully for all references.")
            except Exception as e:
                st.error(f"An error occurred during automation: {e}")
        else:
            st.warning("Please fill in all the fields: username, password, and references.")

if __name__ == "__main__":
    run_streamlit()
