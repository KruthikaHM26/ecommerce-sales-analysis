import streamlit as st
import pandas as pd

# Page settings
st.set_page_config(
    page_title="E-commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 E-commerce Sales Analysis")
st.write("Analyze your sales, cost, and profit easily.")

# Upload CSV file
uploaded_file = st.file_uploader(
    "Upload your ecommerce_sales.csv file",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        if "sales_data" not in st.session_state:
            st.session_state.sales_data = pd.read_csv(uploaded_file)

        df = st.session_state.sales_data.copy()

        # Required columns
        required_columns = [
            "OrderID", "Date", "Product",
            "Category", "Qty", "Price", "Cost"
        ]

        if not all(col in df.columns for col in required_columns):
            st.error("CSV file columns are incorrect. Please check your file.")
            st.write("Required columns:", required_columns)

        else:
            # Add New Sale Form
            st.subheader("➕ Add New Product / Sale")

            with st.form("add_sale_form"):
                product_name = st.text_input("Product Name")
                category_name = st.text_input("Category Name")

                sale_date = st.date_input("Sale Date")

                qty = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=1,
                    step=1
                )

                price = st.number_input(
                    "Price per item (₹)",
                    min_value=0.0,
                    value=100.0
                )

                cost = st.number_input(
                    "Cost per item (₹)",
                    min_value=0.0,
                    value=50.0
                )

                submitted = st.form_submit_button("➕ Add Sale")

                if submitted:
                    if not product_name.strip() or not category_name.strip():
                        st.error("Please enter Product Name and Category Name.")

                    elif cost > price:
                        st.warning(
                            "Cost is greater than Price. "
                            "Please check the values."
                        )

                    else:
                        new_order = {
                            "OrderID": f"ORD{len(df) + 1:03d}",
                            "Date": sale_date.strftime("%d-%m-%Y"),
                            "Product": product_name.strip(),
                            "Category": category_name.strip(),
                            "Qty": qty,
                            "Price": price,
                            "Cost": cost
                        }

                        new_row = pd.DataFrame([new_order])

                        st.session_state.sales_data = pd.concat(
                            [st.session_state.sales_data, new_row],
                            ignore_index=True
                        )

                        st.success("New sale added successfully!")
                        st.rerun()
            # Convert numeric columns
            for col in ["Qty", "Price", "Cost"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            df = df.dropna(subset=["Qty", "Price", "Cost"])

            # Calculate sales, cost, and profit
            df["Sales"] = df["Qty"] * df["Price"]
            df["TotalCost"] = df["Qty"] * df["Cost"]
            df["Profit"] = df["Sales"] - df["TotalCost"]

            df["Date"] = pd.to_datetime(
                df["Date"], dayfirst=True, errors="coerce"
            )

            # Sidebar filters
            st.sidebar.header("Filters")

            categories = st.sidebar.multiselect(
                "Select Category",
                options=sorted(df["Category"].dropna().unique()),
                default=sorted(df["Category"].dropna().unique())
            )

            products = st.sidebar.multiselect(
                "Select Product",
                options=sorted(df["Product"].dropna().unique()),
                default=sorted(df["Product"].dropna().unique())
            )

            filtered_df = df[
                df["Category"].isin(categories)
                & df["Product"].isin(products)
            ]

            # Dashboard summary
            st.subheader("📊 Sales Summary")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Total Sales",
                f"₹{filtered_df['Sales'].sum():,.0f}"
            )

            col2.metric(
                "Total Cost",
                f"₹{filtered_df['TotalCost'].sum():,.0f}"
            )

            col3.metric(
                "Total Profit",
                f"₹{filtered_df['Profit'].sum():,.0f}"
            )

            col4.metric(
                "Total Orders",
                filtered_df["OrderID"].nunique()
            )

            # Product-wise sales chart
            st.subheader("📦 Sales by Product")

            product_sales = filtered_df.groupby(
                "Product"
            )["Sales"].sum().sort_values(ascending=False)

            st.bar_chart(product_sales)

            # Category-wise sales chart
            st.subheader("🏷️ Sales by Category")

            category_sales = filtered_df.groupby(
                "Category"
            )["Sales"].sum().sort_values(ascending=False)

            st.bar_chart(category_sales)

            # Profit chart
            st.subheader("💰 Profit by Product")

            product_profit = filtered_df.groupby(
                "Product"
            )["Profit"].sum().sort_values(ascending=False)

            st.bar_chart(product_profit)

            # Date-wise sales chart
            st.subheader("📅 Date-wise Sales")

            date_sales = (
                filtered_df.dropna(subset=["Date"])
                .groupby("Date")["Sales"]
                .sum()
                .sort_index()
            )

            st.line_chart(date_sales)

            # Data table
            st.subheader("📋 Analyzed Sales Data")
            filtered_df.columns=filtered_df.columns.str.strip()
            st.dataframe(filtered_df, use_container_width=True)

            # Download button
            csv_data = filtered_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download Analyzed CSV",
                data=csv_data,
                file_name="analyzed_sales.csv",
                mime="text/csv"
            )

            # Business insights
            st.subheader("💡 Business Insights")

            if not filtered_df.empty:
                best_product = product_sales.idxmax()
                best_category = category_sales.idxmax()

                st.write(f"🏆 Best-selling product by revenue: *{best_product}*")
                st.write(f"🏷️ Highest-revenue category: *{best_category}*")
            else:
                st.info("No data matches the selected filters.")

    except Exception as e:
        st.error(f"Could not read the CSV file: {e}")

else:
    st.info("Please upload your ecommerce_sales.csv file to view the dashboard.")
