
import streamlit as st
import pdfplumber
import pandas as pd
import os
import tempfile
from pathlib import Path


class PDFExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.products = {}
        self.all_tables = []

    def extract_product_data(self):
        """
        Extracts product data and all tables from the PDF.

        Returns:
            tuple: A tuple containing the product data dictionary and all extracted tables.
        """
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table_num, table in enumerate(tables):
                    self.all_tables.append(table)
                    headers = table[0]
                    for col in range(len(headers)):
                        product_name = headers[col]
                        if product_name and product_name.strip():
                            if product_name not in self.products:
                                self.products[product_name] = {}
                            for row in table[1:]:
                                if len(row) > col:
                                    characteristic = row[0]
                                    value = row[col]
                                    if characteristic and value:
                                        self.products[product_name][characteristic.strip()] = value.strip()
        return self.products, self.all_tables


class ExcelSaver:
    def __init__(self, all_tables):
        self.all_tables = all_tables

    def save_to_tempfile(self):
        """
        Saves the extracted tables to a temporary Excel file.

        Returns:
            str: The path to the temporary Excel file.
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            temp_file_path = temp_file.name
            with pd.ExcelWriter(temp_file_path) as writer:
                row_position = 0
                for table_index, table in enumerate(self.all_tables):
                    df = pd.DataFrame(table[1:], columns=table[0])  # Create DataFrame
                    df.to_excel(writer, sheet_name='Extracted Data', startrow=row_position, index=False, header=True)
                    row_position += len(df) + 2  # Add space between tables
        return temp_file_path


class PDFExtractorApp:
    def __init__(self):
        self.downloads_path = str(Path.home() / "Downloads")

    def run(self):
        """Runs the Streamlit app for PDF extraction."""
        st.set_page_config(page_title="PDF to Excel Extractor", layout="centered")
        st.title("📄 PDF to Excel Extractor")
        st.write("Upload a PDF file to extract tables and save them directly as an Excel file for download.")

        uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

        if uploaded_file:
            self._process_pdf(uploaded_file)
        else:
            st.info("Please upload a PDF file to begin.")

    def _process_pdf(self, uploaded_file):
        """Handles PDF extraction and saving to Excel."""
        if st.button("Extract and Save to Temp File"):
            with st.spinner("Processing the PDF..."):
                try:
                    # Extract data
                    pdf_extractor = PDFExtractor(uploaded_file)
                    _, all_tables = pdf_extractor.extract_product_data()

                    # Save to a temporary Excel file
                    excel_saver = ExcelSaver(all_tables)
                    temp_excel_file = excel_saver.save_to_tempfile()

                    # Provide download link to the user
                    with open(temp_excel_file, "rb") as file:
                        st.download_button(
                            label="Download Excel File",
                            data=file,
                            file_name="Extracted_Tables.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    # Show success message and animation
                    st.success("Data extraction successful! Click the button to download.")
                    st.balloons()  # Display a festive animation for success
                except Exception as e:
                    st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    app = PDFExtractorApp()
    app.run()
