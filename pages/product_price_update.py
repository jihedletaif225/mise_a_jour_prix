
import streamlit as st
from datetime import datetime
from plyer import notification
import pandas as pd
import altair as alt
import re
import tempfile
import sys


class PriceUpdateLogic:
    def __init__(self):
        self.price_changes = []
        self.new_products = []
        self.products_to_deactivate = []

    @staticmethod
    def clean_price(price):
        """Cleans and standardizes a single price string."""
        if price is None or price == "":
            return None
        try:
            cleaned = re.sub(r"[^\d.]", "", str(price))
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

    def compare_files(self, file1, file2):
        """Compares two Excel files and identifies changes, additions, and removals."""
        old_data = pd.read_excel(file1).set_index('Reference').to_dict(orient='index')
        new_data = pd.read_excel(file2).set_index('Reference').to_dict(orient='index')

        for ref in old_data:
            old_data[ref]['Price'] = self.clean_price(old_data[ref].get('Price'))

        for ref in new_data:
            new_data[ref]['Price'] = self.clean_price(new_data[ref].get('Price'))

        price_changes = []
        new_products = []
        products_to_deactivate = []

        for ref, new_row in new_data.items():
            if ref in old_data:
                old_price = old_data[ref].get('Price')
                new_price = new_row.get('Price')
                if old_price != new_price:
                    price_changes.append((ref, old_price, new_price))
            else:
                new_products.append((ref, new_row.get('Price')))

        for ref in old_data:
            if ref not in new_data:
                products_to_deactivate.append(ref)

        self.price_changes = price_changes
        self.new_products = new_products
        self.products_to_deactivate = products_to_deactivate

    def notify_changes(self):
        """Sends a notification summarizing the changes."""
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"price_changes_{today}.txt"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_filename = temp_file.name
            with open(temp_filename, 'w') as f:
                if self.price_changes:
                    f.write(f"{len(self.price_changes)} products have price changes:\n")
                    for ref, old, new in self.price_changes:
                        f.write(f"Reference {ref}: Old Price {old}, New Price {new}\n")
                else:
                    f.write("No price changes detected this week.\n")

                if self.new_products:
                    f.write(f"\n{len(self.new_products)} new products found:\n")
                    for ref, price in self.new_products:
                        f.write(f"Reference {ref}, Price: {price}\n")
                else:
                    f.write("\nNo new products found this week.\n")

                if self.products_to_deactivate:
                    f.write(f"\n{len(self.products_to_deactivate)} products to deactivate:\n")
                    for ref in self.products_to_deactivate:
                        f.write(f"Reference {ref}\n")
                else:
                    f.write("\nNo products to deactivate this week.\n")
        if sys.platform in ['win32', 'darwin', 'linux']:
            try:
                notification_message = (
                    f"Price changes: {len(self.price_changes)}\n"
                    f"New products: {len(self.new_products)}\n"
                    f"Products to deactivate: {len(self.products_to_deactivate)}"
                )

                notification.notify(
                    title="Product Update Summary",
                    message=notification_message,
                    timeout=10
                )
            except Exception as e:
                print(f"Error sending notification: {e}")

        with open(temp_filename, 'r') as file:
            st.download_button(
                label="Download Price Changes Summary",
                data=file.read(),
                file_name=filename,
                mime="text/plain"
            )

    def save_new_products(self):
        """Saves new products to an Excel file."""
        today = datetime.now().strftime("%Y-%m-%d")
        new_file = f"new_products_{today}.xlsx"
        df = pd.DataFrame(self.new_products, columns=['Reference', 'Price'])
        df.to_excel(new_file, index=False)
        print(f"New products saved to {new_file}")


class PriceUpdateAppUI:
    def __init__(self):
        self.logic = PriceUpdateLogic()

    def run(self):
        st.set_page_config(page_title="Product Update App", layout="wide", initial_sidebar_state="expanded")
        st.title("Product Update App")
        st.sidebar.title("Options")

        file1 = st.sidebar.file_uploader("Select the older Excel file", type=["xlsx"])
        file2 = st.sidebar.file_uploader("Select the newer Excel file", type=["xlsx"])

        if file1 and file2:
            self.logic.compare_files(file1, file2)
            self.logic.notify_changes()
            # self.logic.save_new_products()

            st.write(f"Processing completed. {len(self.logic.price_changes)} price changes detected.")

            # Price Changes DataFrame
            st.subheader("Price Changes")
            price_changes_df = pd.DataFrame(self.logic.price_changes, columns=['Reference', 'Old Price', 'New Price'])
            price_changes_df['Old Price'] = price_changes_df['Old Price'].apply(lambda x: f"{x:.2f}")
            price_changes_df['New Price'] = price_changes_df['New Price'].apply(lambda x: f"{x:.2f}")
            # Calculate the Difference between Old Price and New Price
            price_changes_df['Difference'] = price_changes_df['New Price'].apply(pd.to_numeric) - price_changes_df['Old Price'].apply(pd.to_numeric)

            # Format the Difference column to show positive differences with a "+" sign
            price_changes_df['Difference'] = price_changes_df['Difference'].apply(lambda x: f"+{x:.2f}" if x > 0 else f"{x:.2f}")

            # Apply color formatting to the 'Difference' column based on the value
            def color_difference(val):
                color = 'green' if float(val) > 0 else 'red'
                return f'color: {color}'

            # Apply the color formatting function to the 'Difference' column
            # styled_price_changes_df = price_changes_df.style.applymap(color_difference, subset=['Difference'])
            styled_price_changes_df = price_changes_df.style.map(color_difference, subset=['Difference'])

            # Display the Price Changes with color formatting in a table
            st.dataframe(styled_price_changes_df)

            st.subheader("New Products")
            new_products_df = pd.DataFrame(self.logic.new_products, columns=['Reference', 'Price'])

            # Format Prices in the New Products table
            new_products_df['Price'] = new_products_df['Price'].apply(lambda x: f"{x:.2f}")

            st.dataframe(new_products_df)

            st.subheader("Products to Deactivate")
            products_to_deactivate_df = pd.DataFrame({'Reference': self.logic.products_to_deactivate})
            st.dataframe(products_to_deactivate_df)

            st.subheader("Summary")
            summary_data = [
                {'Metric': 'Price Changes', 'Value': len(self.logic.price_changes)},
                {'Metric': 'New Products', 'Value': len(self.logic.new_products)},
                {'Metric': 'Products to Deactivate', 'Value': len(self.logic.products_to_deactivate)}
            ]
            summary_df = pd.DataFrame(summary_data)

            # Change the color for New Products to blue
            chart = alt.Chart(summary_df).mark_bar().encode(
                x='Metric',
                y='Value',
                color=alt.Color(
                'Metric:N',
                scale=alt.Scale(domain=['Price Changes', 'New Products', 'Products to Deactivate'],
                        range=['green', 'blue', 'red'])  # Specify the color mapping for each metric
                )
                ).properties(width=600, height=400)

            st.altair_chart(chart, use_container_width=True)




if __name__ == "__main__":
    app_ui = PriceUpdateAppUI()
    app_ui.run()
