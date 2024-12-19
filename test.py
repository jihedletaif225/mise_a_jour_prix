

import logging
from playwright.async_api import Page, async_playwright
from typing import List
import pandas as pd


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RestauConcept:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    async def login(self, page: Page) -> bool:
        """
        Log in to the RestauConcept admin page.
        
        :param page: Playwright Page object
        :return: True if login is successful, False otherwise
        """
        try:
            await page.goto("https://www.restoconcept.com/admin/logon.asp")
            await page.fill("#adminuser", self.username)
            await page.fill("#adminPass", self.password)
            await page.click("#btn1")
            
            try:
                await page.wait_for_selector('td[align="center"][style="background-color:#eeeeee"]:has-text("© Copyright 2024 - Restoconcept")', timeout=5000)
                return True
            except TimeoutError:
                return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    async def process_marque(self, page: Page, marque: str) -> List[str]:
        """
        Extract edit links for products from a specific supplier.
        
        :param page: Playwright Page object
        :param marque: Supplier/Brand to process
        :return: List of product edit URLs
        """
        await page.goto("https://www.restoconcept.com/admin/SA_prod.asp", wait_until="networkidle")
        
        # Wait and select supplier
        await page.wait_for_selector('select[name="marque"]')
        await page.select_option('select[name="marque"]', marque)
        await page.click('button:has-text("Rechercher")')
        
        # Wait for results
        await page.wait_for_load_state("networkidle")
        
        # Extract the desired data (1st, 2nd, and 8th <td> elements)
        edit_links = []
        while True:
            rows = await page.query_selector_all('table.listTable tr')
            
            for row in rows:
                tds = await row.query_selector_all("td")
                if len(tds) >= 5:  # Make sure there are enough td elements
                    first_td = await tds[0].inner_text()
                    second_td = await tds[1].inner_text()
                    eighth_td = await tds[7].inner_text()
                    
                    # Check if eighth td has the style we are looking fo
                        # Add the values to edit_links
                    edit_links.append({
                            "No": first_td,
                            "Référence": second_td,
                            "Prix public": eighth_td
                        })

            # Check for next page
            next_links = await page.locator('a:has-text("Suiv.")').all()
            if not next_links:
                break

            try:
                await next_links[0].click()
                await page.wait_for_load_state("networkidle")
            except Exception as e:
                logger.error(f"Error navigating to next page: {e}")
                break

        logger.info(f"Total product links found for {marque}: {len(edit_links)}")
        
        # Optionally print the extracted links for debugging purposes
        logger.info(f"Extracted links: {edit_links}")
        return edit_links

# Main function to run the login and processing logic
async def main():
    username = "letaief"  # Replace with your username
    password = "mohamed jihe"  # Replace with your password
    marque = "RM GASTRO"  # Replace with your supplier/brand to process

    # Create an instance of RestauConcept
    restau_concept = RestauConcept(username, password)

    # Start Playwright and interact with the page
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True for no UI
        page = await browser.new_page()

        # Perform login
        login_success = await restau_concept.login(page)
        if login_success:
            logger.info("Login successful")
        else:
            logger.error("Login failed")
            await browser.close()
            return

        # Process the specified marque and get the product links
        edit_links = await restau_concept.process_marque(page, marque)
        if edit_links:
            logger.info(f"Found {len(edit_links)} product links for marque {marque}")
            for link in edit_links:
                logger.info(link)
            
             # Save to Excel
            df = pd.DataFrame(edit_links)
            output_file = f"{marque}_products.xlsx"
            df.to_excel(output_file, index=False)
            logger.info(f"Saved product links to {output_file}")

        else:
            logger.info(f"No products found for marque {marque}")

           


        # Close the browser
        await browser.close()

# Run the main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
