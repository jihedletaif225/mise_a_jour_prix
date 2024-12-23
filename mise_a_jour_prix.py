


import streamlit as st
from datetime import datetime
# import openpyxl
from plyer import notification
import pandas as pd
import altair as alt
import re

def clean_price(price):
    """
    Cleans and standardizes a single price string.
    
    Args:
        price (str): The price string to clean.
        
    Returns:
        float: The cleaned price as a float, or None if invalid.
    """
    if price is None or price == "":  # Handle missing values
        return None
    try:
        # Remove all non-numeric characters except for the decimal point
        cleaned = re.sub(r"[^\d.]", "", str(price))
        # Convert to float
        return float(cleaned) if cleaned else None
    except ValueError:
        return None
def compare_files(file1, file2):
    old_wb = pd.read_excel(file1)
    new_wb = pd.read_excel(file2)
    old_sheet = old_wb.active
    new_sheet = new_wb.active
    
    price_changes = []
    new_products = []
    products_to_deactivate = []
    
    old_data = {old_sheet[f'A{i}'].value: old_sheet[f'C{i}'].value for i in range(2, old_sheet.max_row + 1)}
    new_data = {new_sheet[f'A{i}'].value: new_sheet[f'C{i}'].value for i in range(2, new_sheet.max_row + 1)}
    
    # Check for price changes and new products
    for ref, new_price in new_data.items():
        if ref in old_data:
            old_price = old_data[ref]
            if old_price != new_price:
                price_changes.append((ref, old_price, new_price))
        else:
            # If the product reference is new
            new_products.append((ref, new_price))
    
    # Check for products to deactivate
    for ref in old_data:
        if ref not in new_data:
            products_to_deactivate.append(ref)
    
    return price_changes, new_products, products_to_deactivate

def notify_changes(price_changes, new_products, products_to_deactivate):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"price_changes_{today}.txt"
    
    with open(filename, 'w') as f:
        if price_changes:
            f.write(f"{len(price_changes)} products have price changes:\n")
            for ref, old, new in price_changes:
                diff = clean_price(new) - clean_price(old)
                f.write(f"Reference {ref}: Old Price {old}, New Price {new}, Difference: {diff}\n")
        else:
            f.write("No price changes detected this week.\n")
        
        f.write("\n")  # Add a blank line for separation
        
        if new_products:
            f.write(f"{len(new_products)} new products found:\n")
            for ref, price in new_products:
                f.write(f"Reference {ref}, Price: {price}\n")
        else:
            f.write("No new products found this week.\n")
        
        f.write("\n")  # Add a blank line for separation
        
        if products_to_deactivate:
            f.write(f"{len(products_to_deactivate)} products to deactivate:\n")
            for ref in products_to_deactivate:
                f.write(f"Reference {ref}\n")
        else:
            f.write("No products to deactivate this week.\n")
    print(f"Detailed information has been written to {filename}")
    # Prepare notification message
    notification_message = (
        f"Price changes: {len(price_changes)}\n"
        f"New products: {len(new_products)}\n"
        f"Products to deactivate: {len(products_to_deactivate)}\n"
        f"Details in {filename}"
    )
    # Show notification with plyer (persistent until dismissed manually)
    notification.notify(
        title="Product Update Summary",
        message=notification_message,
        timeout=36000  # This keeps the notification until manually dismissed
    )
    return len(price_changes)

def save_new_products(new_products):
    today = datetime.now().strftime("%Y-%m-%d")
    new_file = f"new_products_{today}.xlsx"
    
    df = pd.DataFrame(new_products, columns=['Reference', 'Price'])
    df.to_excel(new_file, index=False)
    print(f"New products saved to {new_file}")

def main():
    st.set_page_config(page_title="Product Update App", layout="wide", initial_sidebar_state="expanded")

    st.title("Product Update App")
    st.sidebar.title("Options")

    # Prompt user to select the two Excel files
    file1 = st.sidebar.file_uploader("Select the older Excel file", type=["xlsx"])
    file2 = st.sidebar.file_uploader("Select the newer Excel file", type=["xlsx"])

    if file1 and file2:
        # Call the compare_files function
        price_changes, new_products, products_to_deactivate = compare_files(file1, file2)

        # Call the notify_changes function
        num_price_changes = notify_changes(price_changes, new_products, products_to_deactivate)

        # Call the save_new_products function
        save_new_products(new_products)

        st.write(f"Processing completed. {num_price_changes} price changes detected.")

        # Display the results
        st.subheader("Price Changes")
        price_changes_df = pd.DataFrame(price_changes, columns=['Reference', 'Old Price', 'New Price'])
        price_changes_df['Difference'] = price_changes_df['New Price'] - price_changes_df['Old Price']
        price_changes_df['Difference'] = price_changes_df['Difference'].apply(lambda x: f"+{x:.2f}" if x > 0 else f"{x:.2f}")
        
        # Convert 'Difference' to string before applying the style
        price_changes_df = price_changes_df.style.applymap(
            lambda x: 'color:green' if isinstance(x, str) and x.startswith('+') else 'color:red',
            subset=['Difference']
        )
        
        st.dataframe(price_changes_df)

        st.subheader("New Products")
        new_products_df = pd.DataFrame(new_products, columns=['Reference', 'Price'])
        st.dataframe(new_products_df)

        st.subheader("Products to Deactivate")
        products_to_deactivate_df = pd.DataFrame({'Reference': products_to_deactivate})
        st.dataframe(products_to_deactivate_df)

        # Display a summary chart
        st.subheader("Summary")
        summary_data = [
            {'Metric': 'Price Changes', 'Value': num_price_changes},
            {'Metric': 'New Products', 'Value': len(new_products)},
            {'Metric': 'Products to Deactivate', 'Value': len(products_to_deactivate)}
        ]
        summary_df = pd.DataFrame(summary_data)
        chart = alt.Chart(summary_df).mark_bar().encode(
            x='Metric',
            y='Value',
            color=alt.condition(
                alt.datum.Metric == 'Price Changes',
                alt.value('green'),
                alt.value('red')
            )
        ).properties(
            width=600,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()