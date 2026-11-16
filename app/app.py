import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
st.set_page_config(
    page_title="OLA Ride Insights",
    page_icon="🚖",
    layout="wide"
)

@st.cache_data
def load_data():
    data_path = Path(__file__).resolve().parents[1] / "Data" / "ola_cleaned.csv"
    df = pd.read_csv(data_path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Day_Number"] = df["Date"].dt.day

    return df

df = load_data()

st.title("🚖 OLA Ride Insights Dashboard")
st.write("Interactive analysis of ride bookings, revenue, cancellations, and ratings.")

# Sidebar filters
st.sidebar.header("Filters")

booking_status = st.sidebar.multiselect(
    "Booking Status",
    options=sorted(df["Booking_Status"].dropna().unique()),
    default=sorted(df["Booking_Status"].dropna().unique())
)

vehicle_type = st.sidebar.multiselect(
    "Vehicle Type",
    options=sorted(df["Vehicle_Type"].dropna().unique()),
    default=sorted(df["Vehicle_Type"].dropna().unique())
)

payment_method = st.sidebar.multiselect(
    "Payment Method",
    options=sorted(df["Payment_Method"].dropna().unique()),
    default=sorted(df["Payment_Method"].dropna().unique())
)

filtered_df = df[
    (df["Booking_Status"].isin(booking_status)) &
    (df["Vehicle_Type"].isin(vehicle_type)) &
    (df["Payment_Method"].isin(payment_method))
]

# KPI cards
total_rides = len(filtered_df)
total_revenue = filtered_df["Booking_Value"].sum()
average_distance = filtered_df["Ride_Distance"].mean()
success_rate = (
    (filtered_df["Booking_Status"] == "Success").mean() * 100
    if total_rides > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Rides", f"{total_rides:,}")
col2.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col3.metric("Average Ride Distance", f"{average_distance:.2f} km")
col4.metric("Success Rate", f"{success_rate:.2f}%")

st.divider()

# Charts
left, right = st.columns(2)

with left:
    rides_by_day = (
        filtered_df.groupby("Day_Number")
        .size()
        .reset_index(name="Ride Count")
    )

    fig_rides = px.line(
        rides_by_day,
        x="Day_Number",
        y="Ride Count",
        markers=True,
        title="Ride Volume Over Time"
    )
    st.plotly_chart(fig_rides, use_container_width=True)

with right:
    status_data = (
        filtered_df.groupby("Booking_Status")
        .size()
        .reset_index(name="Ride Count")
    )

    fig_status = px.pie(
        status_data,
        names="Booking_Status",
        values="Ride Count",
        hole=0.45,
        title="Booking Status Breakdown"
    )
    st.plotly_chart(fig_status, use_container_width=True)

left, right = st.columns(2)

with left:
    revenue_payment = (
        filtered_df.groupby("Payment_Method")["Booking_Value"]
        .sum()
        .reset_index()
    )

    fig_payment = px.bar(
        revenue_payment,
        x="Payment_Method",
        y="Booking_Value",
        color="Payment_Method",
        title="Revenue by Payment Method"
    )
    st.plotly_chart(fig_payment, use_container_width=True)

with right:
    rating_data = (
        filtered_df.groupby("Vehicle_Type")[["Driver_Ratings", "Customer_Rating"]]
        .mean()
        .reset_index()
        .melt(
            id_vars="Vehicle_Type",
            value_vars=["Driver_Ratings", "Customer_Rating"],
            var_name="Rating Type",
            value_name="Average Rating"
        )
    )

    fig_ratings = px.bar(
        rating_data,
        x="Vehicle_Type",
        y="Average Rating",
        color="Rating Type",
        barmode="group",
        title="Customer vs Driver Ratings"
    )
    st.plotly_chart(fig_ratings, use_container_width=True)

st.divider()

# SQL query results section
st.header("SQL Query Results")

query_choice = st.selectbox(
    "Choose a required SQL query",
    [
        "1. Successful bookings",
        "2. Average ride distance by vehicle type",
        "3. Customer-cancelled rides",
        "4. Top 5 customers by number of rides",
        "5. Driver personal/car-related cancellations",
        "6. Prime Sedan max/min driver ratings",
        "7. UPI payments",
        "8. Average customer rating by vehicle type",
        "9. Successful ride booking value",
        "10. Incomplete rides with reason"
    ]
)

if query_choice.startswith("1."):
    result = filtered_df[
        filtered_df["Booking_Status"] == "Success"
    ]

elif query_choice.startswith("2."):
    result = (
        filtered_df.groupby("Vehicle_Type")["Ride_Distance"]
        .mean()
        .round(2)
        .reset_index(name="Average Ride Distance")
    )

elif query_choice.startswith("3."):
    result = pd.DataFrame({
        "Customer Cancelled Rides": [
            len(filtered_df[
                filtered_df["Booking_Status"] == "Canceled by Customer"
            ])
        ]
    })

elif query_choice.startswith("4."):
    result = (
        filtered_df.groupby("Customer_ID")
        .size()
        .reset_index(name="Total Rides")
        .sort_values("Total Rides", ascending=False)
        .head(5)
    )

elif query_choice.startswith("5."):
    result = pd.DataFrame({
        "Driver Personal/Car Cancellations": [
            len(filtered_df[
                filtered_df["Canceled_Rides_by_Driver"] ==
                "Personal & Car related issue"
            ])
        ]
    })

elif query_choice.startswith("6."):
    prime_sedan = filtered_df[
        filtered_df["Vehicle_Type"] == "Prime Sedan"
    ]

    result = pd.DataFrame({
        "Maximum Driver Rating": [prime_sedan["Driver_Ratings"].max()],
        "Minimum Driver Rating": [prime_sedan["Driver_Ratings"].min()]
    })

elif query_choice.startswith("7."):
    result = filtered_df[
        filtered_df["Payment_Method"] == "UPI"
    ]

elif query_choice.startswith("8."):
    result = (
        filtered_df.groupby("Vehicle_Type")["Customer_Rating"]
        .mean()
        .round(2)
        .reset_index(name="Average Customer Rating")
    )

elif query_choice.startswith("9."):
    result = pd.DataFrame({
        "Total Successful Booking Value": [
            filtered_df.loc[
                filtered_df["Booking_Status"] == "Success",
                "Booking_Value"
            ].sum()
        ]
    })

else:
    result = filtered_df[
        filtered_df["Incomplete_Rides"] == "Yes"
    ][
        ["Booking_ID", "Incomplete_Rides", "Incomplete_Rides_Reason"]
    ]

st.dataframe(result, use_container_width=True)