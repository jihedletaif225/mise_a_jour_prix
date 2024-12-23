

import logging
from playwright.async_api import async_playwright

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
            # Navigate to login page
            await page.goto("https://www.restoconcept.com/admin/logon.asp")
            # Fill login credentials
            await page.fill("#adminuser", self.username)
            await page.fill("#adminPass", self.password)
            # Click login button
            await page.click("#btn1")

            try:
                # Wait for the page to load after login
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

    async def perform_search_and_uncheck(self, page) -> bool:
        try:
            logger.info("Navigating to the search page...")
            # Navigate to the search page
            await page.goto("https://www.restoconcept.com/admin/marges.asp")
            
            logger.info("Entering reference number...")
            # Enter the reference number into the input field
            reference_input_selector = 'input[name="rch_phrase"]'
            await page.fill(reference_input_selector, "6775987")

            logger.info("Clicking the search button...")
            # Click the search button
            search_button_selector = 'button[type="submit"]'
            await page.click(search_button_selector)

            logger.info("Waiting for checkbox to appear...")
            # Wait for the checkbox to appear after search
            checkbox_selector = 'td[style="padding:4px; border:1px #666 solid; text-align:center;"] input[type="checkbox"][name="active"]'

            try:
                # Wait for the checkbox to be visible
                await page.wait_for_selector(checkbox_selector, timeout=5000)
                logger.info("Checkbox is visible.")
                
                # Check if the checkbox is checked
                checkbox = await page.query_selector(checkbox_selector)
                is_checked = await checkbox.get_attribute("checked")
                logger.info(f"Checkbox checked attribute: {is_checked}")
                
                # If checked, uncheck it
                # if is_checked is not None:
                    # logger.info("Unchecking the checkbox...")
                await checkbox.uncheck()
                    
                    # Selector for the "Actualiser" input button
                actualiser_button_selector = 'td[style="padding:4px; border:1px #666 solid; text-align:center;"] input[type="submit"][value="Actualiser"]'
                    
                logger.info("Clicking the 'Actualiser' button...")
                    # Click the "Actualiser" button
                await page.click(actualiser_button_selector)

                logger.info("Checkbox unchecked and 'Actualiser' button clicked successfully.")
                return True
                # else:
                #     logger.info("Checkbox is already unchecked.")
                #     return True
            except Exception as e:
                logger.error(f"Error while interacting with checkbox: {e}")
                return False
        except Exception as e:
            logger.error(f"Error during search and uncheck: {e}")
            return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # You can change to True for headless mode
        page = await browser.new_page()

        # Replace with actual credentials
        username = "letaief"
        password = "mohamed jihe"

        automation = RestoconceptAutomation(username, password)

        # Login
        logged_in = await automation.login(page)
        if logged_in:
            logger.info("Login successful.")
            # Perform search and uncheck checkbox
            result = await automation.perform_search_and_uncheck(page)
            if result:
                logger.info("Task completed successfully.")
            else:
                logger.error("Failed to complete the task.")
        else:
            logger.error("Login failed.")

        await browser.close()

# Run the automation
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
