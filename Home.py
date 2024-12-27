import streamlit as st
import os
import platform
import subprocess
from subprocess import run, CalledProcessError
import sys

# Ensure correct event loop policy for Windows
if platform.system() == "Windows":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


st.set_page_config(
    page_title="RestauConcept Admin Tools",
    page_icon="🛠️",
    layout="centered"
)

# Header with Icon
st.title("🛠️ RestauConcept Admin Tools")
st.markdown("<br>", unsafe_allow_html=True)

# Welcome Section
st.markdown("""
## Welcome! 👋
This application provides powerful tools to manage and streamline your administrative tasks for RestauConcept.  
Use the **sidebar** to navigate between the available functionalities:
""")

# Feature Highlights
st.markdown("""
### Available Tools:
- **🔍 Data Scraper**: Extract product information quickly and efficiently.
- **❌ Product Deactivation**: Easily deactivate outdated products.
- **📄 PDF to Excel Extractor**: Convert PDF data into Excel format for seamless integration.
- **💲 Price Update**: Update product prices in bulk with ease.
""")

# Decorative Image or Logo (Optional)
st.image("https://via.placeholder.com/800x200?text=RestauConcept+Admin+Tools", use_container_width=True)

# Instruction Section
st.markdown("""
---
### How to Use:
1. Select the desired functionality from the **sidebar** on the left.
2. Follow the on-screen instructions for each tool.
3. Have questions? Check the documentation or reach out for support.
""")

# Footer or Contact Info
st.markdown("""
---
**Contact Support**:  
📧 Email: [support@restauconcept.com](mailto:support@restauconcept.com)  
📞 Phone: +1-234-567-890
""")
