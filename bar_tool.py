import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Bar Sales Tracker", layout="centered")

# Initialize session state
if 'sales' not in st.session_state:
    st.session_state.sales = []

if 'current_order' not in st.session_state:
    st.session_state.current_order = []

if 'show_other_fields' not in st.session_state:
    st.session_state.show_other_fields = False

# Drinks and prices (EUR)
drink_options = {
    '🍺 Beer': 3.5,
    '🌿 Arak': 4.0,
    '🍾 Wine Bottle': 35.0,
    '🍷 Wine Glass': 8.0,
    '🔥 Doudou Shots': 2.0,
    '🥤 Soft Drink': 3.0,
    '➕ Other': None  # Placeholder for the custom item
}

# Tabs
tab1, tab2 = st.tabs(["🧾 Order Entry", "📊 Sales Dashboard"])

# === TAB 1: ORDER ENTRY ===
with tab1:
    st.title("Create Order")

    st.markdown("### Tap drinks to add to the order:")
    cols = st.columns(3)
    for idx, (drink, price) in enumerate(drink_options.items()):
        with cols[idx % 3]:
            if st.button(f"{drink}\n€{price:.2f}" if price else f"{drink}", key=f"btn_{drink}"):
                if drink == '➕ Other':
                    st.session_state.show_other_fields = True
                else:
                    st.session_state.current_order.append({"drink": drink, "price": price})
                    st.success(f"Added {drink}")

    # Show "Other" input fields only when triggered
    if st.session_state.show_other_fields:
        st.markdown("### Add 'Other' Item:")
        custom_desc = st.text_input("Description", key="desc")
        custom_price = st.number_input("Price (EUR)", min_value=0.0, step=0.5, key="price")

        if st.button("➕ Add Custom Item"):
            if custom_desc and custom_price > 0:
                st.session_state.current_order.append({
                    "drink": f"Other: {custom_desc}",
                    "price": custom_price
                })
                st.success(f"Added custom item: {custom_desc}")
                st.session_state.show_other_fields = False
                st.rerun()
            else:
                st.warning("Please enter a valid description and price.")

    # Show current order with delete buttons
    st.markdown("### 🛒 Current Order")
    if st.session_state.current_order:
        for i, item in enumerate(st.session_state.current_order):
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.write(item["drink"])
            with col2:
                st.write(f"€{item['price']:.2f}")
            with col3:
                if st.button("❌", key=f"delete_{i}"):
                    del st.session_state.current_order[i]
                    st.rerun()
        if st.button("✅ Submit Order"):
            now = datetime.now()
            for item in st.session_state.current_order:
                st.session_state.sales.append({
                    "drink": item["drink"],
                    "price": item["price"],
                    "timestamp": now
                })
            st.success("Order submitted successfully!")
            st.session_state.current_order = []
    else:
        st.info("No items selected yet.")

# === TAB 2: DASHBOARD ===
with tab2:
    st.title("Sales Dashboard")

    if not st.session_state.sales:
        st.info("No sales recorded yet.")
    else:
        df = pd.DataFrame(st.session_state.sales)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['time'] = df['timestamp'].dt.strftime("%H:%M:%S")

        st.subheader("🧾 Order Log")
        st.dataframe(df[['time', 'drink', 'price']], use_container_width=True)

        st.subheader("📈 Summary")
        total_sales = df['price'].sum()
        drink_counts = df['drink'].value_counts()
        st.metric("Total Sales (EUR)", f"€{total_sales:.2f}")
        st.bar_chart(drink_counts)

        st.download_button("⬇️ Download CSV", df.to_csv(index=False), "sales_report.csv")

