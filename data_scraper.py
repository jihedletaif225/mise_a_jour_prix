
import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging
from asyncio import ProactorEventLoop
import platform


if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RestauConcept:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    async def login(self, page) -> bool:
        try:
            await page.goto("https://www.restoconcept.com/admin/logon.asp")
            await page.fill("#adminuser", self.username)
            await page.fill("#adminPass", self.password)
            await page.click("#btn1")

            try:
                await page.wait_for_selector('td[align="center"][style="background-color:#eeeeee"]:has-text("© Copyright 2024 - Restoconcept")', timeout=5000)
                return True
            except:
                return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    async def process_marque(self, page, marque: str):
        await page.goto("https://www.restoconcept.com/admin/SA_prod.asp", wait_until="networkidle")
        await page.select_option('select[name="marque"]', marque)
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
            try:
                await next_links[0].click()
                await page.wait_for_load_state("networkidle")
            except Exception as e:
                logger.error(f"Error navigating to next page: {e}")
                break

        return edit_links


async def scrape_data(username, password, marque):
    restau_concept = RestauConcept(username, password)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        if await restau_concept.login(page):
            links = await restau_concept.process_marque(page, marque)
            await browser.close()
            return links
        else:
            await browser.close()
            return None


# Streamlit UI
st.title("RestauConcept Data Scraper")
st.sidebar.header("User Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
marque = st.sidebar.text_input("Supplier/Brand (Marque)")

if st.sidebar.button("Start Scraping"):
    if not username or not password or not marque:
        st.error("Please fill out all fields.")
    else:
        with st.spinner("Scraping data, please wait..."):
            try:
                links = asyncio.run(scrape_data(username, password, marque))
                if links:
                    st.success(f"Found {len(links)} products for marque {marque}.")
                    st.write(pd.DataFrame(links))

                    # Export to Excel
                    output_file = f"{marque}_products.xlsx"
                    df = pd.DataFrame(links)
                    df.to_excel(output_file, index=False)

                    with open(output_file, "rb") as file:
                        st.download_button("Download Excel File", file, file_name=output_file)
                else:
                    st.warning("No products found or login failed.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.sidebar.markdown("""
---
**Instructions:**
1. Enter your username and password.
2. Input the supplier/brand (marque).
3. Click "Start Scraping" to fetch the data.
""")
