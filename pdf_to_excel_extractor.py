


import streamlit as st
import pdfplumber
import pandas as pd
import os
from pathlib import Path

def extract_product_data(pdf_path):
    products = {}
    all_tables = []  # List to store all tables from the PDF

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table_num, table in enumerate(tables):
                all_tables.append(table)
                headers = table[0]
                for col in range(len(headers)):
                    product_name = headers[col]
                    if product_name and product_name.strip():
                        if product_name not in products:
                            products[product_name] = {}
                        for row in table[1:]:
                            if len(row) > col:
                                characteristic = row[0]
                                value = row[col]
                                if characteristic and value:
                                    products[product_name][characteristic.strip()] = value.strip()
    return products, all_tables

def save_tables_to_excel(all_tables, excel_path):
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        row_position = 0  # Track the current row position in the Excel sheet
        for table_index, table in enumerate(all_tables):
            df = pd.DataFrame(table[1:], columns=table[0])  # Create DataFrame from the table, excluding headers
            df.to_excel(writer, sheet_name='Extracted Data', startrow=row_position, index=False, header=True)
            row_position += len(df) + 2  # Add space between tables

# Streamlit App
st.set_page_config(page_title="PDF to Excel Extractor", layout="centered")

st.title("📄 PDF to Excel Extractor")
st.write("Upload a PDF file to extract tables and save them directly to your Downloads folder as an Excel file.")

uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_file:
    # Get the Downloads folder path
    downloads_path = str(Path.home() / "Downloads")
    
    # Default filename for the output Excel file
    excel_file = os.path.join(downloads_path, "Extracted_Tables.xlsx")
    
    if st.button("Extract and Save to Downloads"):
        with st.spinner("Processing the PDF..."):
            try:
                # Extract product data
                _, all_tables = extract_product_data(uploaded_file)
                
                # Save tables to Excel in the Downloads folder
                save_tables_to_excel(all_tables, excel_file)
                
                st.success(f"Data successfully saved to {excel_file}")
                st.balloons()  # Add a festive animation for success
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("Please upload a PDF file to begin.")