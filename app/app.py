from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="OLA Ride Insights", page_icon="🚕", layout="wide",
                   initial_sidebar_state="collapsed")
# Optional: paste your Power BI "Publish to web" link here
POWERBI_URL = ""


# ---------------- Colors ----------------
YELLOW, DARK, GREEN, RED, ORANGE, BLUE, GREY = (
    "#F5C518", "#111827", "#16A34A", "#EF4444", "#F97316", "#3B82F6", "#9CA3AF")
STATUS_COLORS = {"Success": GREEN, "Canceled by Customer": ORANGE,
                 "Canceled by Driver": RED, "Driver Not Found": GREY}
PALETTE = [BLUE, YELLOW, GREEN, ORANGE, RED, "#8B5CF6", "#14B8A6"]
CHART_H = 290  # chart height in pixels; make smaller to fit more on screen

# ---------------- Styling (CSS) ----------------
st.markdown(f"""
<style>
/* use the full screen width, no side gap */
.block-container {{max-width: 100% !important; padding: 0.6rem 1.2rem 0.5rem 1.2rem !important;}}
[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] {{display: none;}}
header[data-testid="stHeader"] {{display: none;}}
[data-testid="stVerticalBlock"] {{gap: 0.55rem;}}
[data-testid="stHorizontalBlock"] {{gap: 0.7rem;}}

.banner {{background: linear-gradient(120deg, {DARK} 0%, #1F2937 60%, #374151 100%);
  padding: 10px 20px; border-radius: 12px; border-left: 6px solid {YELLOW};
  display: flex; align-items: baseline; gap: 16px;}}
.banner h1 {{color: {YELLOW}; margin: 0; padding: 0; font-size: 1.5rem;}}
.banner p {{color: #D1D5DB; margin: 0; font-size: 0.85rem;}}

.kpi {{background: #FFFFFF; border-radius: 12px; padding: 8px 14px;
  box-shadow: 0 1px 6px rgba(17,24,39,0.08); border-top: 4px solid var(--c);}}
.kpi .label {{color: #6B7280; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: .04em;}}
.kpi .value {{color: {DARK}; font-size: 1.45rem; font-weight: 800; line-height: 1.2;}}

.insight {{background: #FFFBEB; border-left: 4px solid {YELLOW}; padding: 7px 12px;
  border-radius: 8px; color: #374151; font-size: 0.9rem;}}
[data-testid="stPlotlyChart"], [data-testid="stPlotlyChart"] > div {{overflow: hidden !important;}}
.banner {{margin-bottom: 8px;}}

/* every chart becomes a white card */
[data-testid="stPlotlyChart"] {{background: #FFFFFF; border-radius: 12px; padding: 4px;
  box-shadow: 0 1px 6px rgba(17,24,39,0.06);}}

/* tabs */
.stTabs [data-baseweb="tab-list"] {{gap: 6px; margin-bottom: 4px;}}
.stTabs [data-baseweb="tab"] {{background: #FFFFFF; border-radius: 8px; padding: 4px 14px; height: 36px; font-weight: 600;}}
.stTabs [aria-selected="true"] {{background: {DARK};}}
.stTabs [aria-selected="true"] p {{color: {YELLOW};}}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{display: none;}}

/* filter box */
[data-testid="stExpander"] {{background: #FFFFFF; border-radius: 12px; border: none; box-shadow: 0 1px 6px rgba(17,24,39,0.06);}}
[data-testid="stExpander"] summary {{padding: 6px 14px;}}
[data-testid="stExpander"] details > div {{padding-top: 0;}}
</style>
""", unsafe_allow_html=True)


# ---------------- Load data ----------------
def find_csv():
    here = Path(__file__).resolve().parent
    for folder in (here, here.parent):
        file = folder / "Data" / "ola_cleaned.csv"
        if file.exists():
            return str(file)
    st.error("Could not find Data/ola_cleaned.csv")
    st.stop()


@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.drop(columns=["Vehicle Images"], errors="ignore")
    for col in ["Booking_Status", "Vehicle_Type", "Payment_Method"]:
        data[col] = data[col].fillna("Not Applicable")
    return data


@st.cache_resource
def make_sql_connection(path):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    table = load_data(path).copy()
    table["Date"] = table["Date"].dt.strftime("%Y-%m-%d")
    table.to_sql("ola_rides", conn, index=False)
    return conn


csv_path = find_csv()
full = load_data(csv_path)

# ---------------- Banner ----------------
st.markdown("""
<div class="banner"><h1>🚕 OLA Ride Insights</h1>
<p>Bookings, revenue, cancellations and ratings. Click the options below to filter.</p></div>
""", unsafe_allow_html=True)

# ---------------- Filter bar (top, click to select) ----------------
OPTIONS = {
    "f_status": sorted(full["Booking_Status"].unique()),
    "f_vehicle": sorted(full["Vehicle_Type"].unique()),
    "f_payment": sorted(full["Payment_Method"].unique()),
}
min_date, max_date = full["Date"].min().date(), full["Date"].max().date()


def reset_filters():
    for key, opts in OPTIONS.items():
        st.session_state[key] = opts
    st.session_state["f_dates"] = (min_date, max_date)
    st.session_state["f_search"] = ""


for key, opts in OPTIONS.items():
    st.session_state.setdefault(key, opts)
st.session_state.setdefault("f_dates", (min_date, max_date))

with st.expander("🎛️ Filters (click to open or close)", expanded=True):
    a, b, c = st.columns([2, 2, 1])
    dates = a.date_input("📅 Date range", min_value=min_date, max_value=max_date, key="f_dates")
    search = b.text_input("🔍 Search Booking ID / Customer ID", key="f_search")
    c.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    c.button("↺ Reset filters", on_click=reset_filters)

    p1, p2, p3 = st.columns([3, 4, 3])
    status = p1.pills("📌 Booking status", OPTIONS["f_status"], selection_mode="multi", key="f_status")
    vehicle = p2.pills("🚗 Vehicle type", OPTIONS["f_vehicle"], selection_mode="multi", key="f_vehicle")
    payment = p3.pills("💳 Payment method", OPTIONS["f_payment"], selection_mode="multi", key="f_payment")

df = full[full["Booking_Status"].isin(status or [])
          & full["Vehicle_Type"].isin(vehicle or [])
          & full["Payment_Method"].isin(payment or [])]
if isinstance(dates, tuple) and len(dates) == 2:
    df = df[(df["Date"].dt.date >= dates[0]) & (df["Date"].dt.date <= dates[1])]
if search:
    df = df[df["Booking_ID"].astype(str).str.contains(search, case=False, regex=False)
            | df["Customer_ID"].astype(str).str.contains(search, case=False, regex=False)]

if df.empty:
    st.warning("No rides match the selected filters. Click '↺ Reset filters'.")
    st.stop()


# ---------------- Helpers ----------------
def kpi(col, label, value, color):
    col.markdown(f'<div class="kpi" style="--c:{color}"><div class="label">{label}</div>'
                 f'<div class="value">{value}</div></div>', unsafe_allow_html=True)


def show(fig, height=CHART_H):
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=8, r=8, t=42, b=8),
                      title_font=dict(size=14, color=DARK), legend_title_text="",
                      font=dict(family="Arial", size=11), colorway=PALETTE)
    st.plotly_chart(fig, config={"displayModeBar": False})


def insight(text):
    st.markdown(f'<div class="insight">💡 {text}</div>', unsafe_allow_html=True)


is_cancel = df["Booking_Status"].str.contains("Cancel", case=False)
c1, c2, c3, c4, c5 = st.columns(5)
kpi(c1, "Total rides", f"{len(df):,}", BLUE)
kpi(c2, "Revenue (successful rides)", f"₹{df.loc[df['Booking_Status'] == 'Success', 'Booking_Value'].sum():,.0f}", GREEN)
kpi(c3, "Avg ride distance", f"{df['Ride_Distance'].mean():.1f} km", YELLOW)
kpi(c4, "Success rate", f"{(df['Booking_Status'] == 'Success').mean() * 100:.1f}%", GREEN)
kpi(c5, "Cancellation rate", f"{is_cancel.mean() * 100:.1f}%", RED)

tabs = st.tabs(["📊 Overview", "🚗 Vehicles", "💰 Revenue", "❌ Cancellations",
                "⭐ Ratings", "🧮 SQL Explorer", "📈 Power BI"])

# ---------------- Overview ----------------
with tabs[0]:
    left, right = st.columns([3, 2])
    daily = df.groupby(df["Date"].dt.date).size().reset_index()
    daily.columns = ["Date", "Rides"]
    fig = px.area(daily, x="Date", y="Rides", title="Ride Volume Over Time")
    fig.update_traces(line_color=BLUE, fillcolor="rgba(59,130,246,0.15)")
    with left:
        show(fig)
    counts = df["Booking_Status"].value_counts().rename_axis("Status").reset_index(name="Rides")
    with right:
        show(px.pie(counts, names="Status", values="Rides", hole=0.55, color="Status",
                    color_discrete_map=STATUS_COLORS, title="Booking Status Breakdown"))

    by_hour = df.groupby("Hour").size().reset_index(name="Rides")
    peak = by_hour.loc[by_hour["Rides"].idxmax(), "Hour"]
    per_day = df.groupby("Day_Name")["Date"].apply(lambda s: s.dt.date.nunique())
    best_day = (df["Day_Name"].value_counts() / per_day).idxmax()
    insight(f"Peak demand is around <b>{int(peak)}:00</b>, and <b>{best_day}</b> is the busiest day. "
            "Put more drivers on the road at these times.")
    a, b = st.columns(2)
    with a:
        show(px.bar(by_hour, x="Hour", y="Rides", title="Rides by Hour of Day"))
    heat = df.groupby(["Day_Name", "Hour"]).size().reset_index(name="Rides")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    with b:
        show(px.density_heatmap(heat, x="Hour", y="Day_Name", z="Rides", color_continuous_scale="YlOrRd",
                                category_orders={"Day_Name": days}, title="Demand Heatmap (Day vs Hour)"))

# ---------------- Vehicles ----------------
with tabs[1]:
    left, right = st.columns(2)
    top5 = df.groupby("Vehicle_Type")["Ride_Distance"].sum().nlargest(5).reset_index()
    with left:
        show(px.bar(top5, x="Vehicle_Type", y="Ride_Distance", text_auto=".3s",
                    title="Top 5 Vehicle Types by Ride Distance"), 380)
    avg_cust = df.groupby("Vehicle_Type")["Customer_Rating"].mean().reset_index()
    with right:
        show(px.bar(avg_cust, x="Vehicle_Type", y="Customer_Rating", text_auto=".2f",
                    title="Average Customer Rating by Vehicle Type"), 380)
    insight(f"<b>{top5.iloc[0]['Vehicle_Type']}</b> covers the most total distance.")

# ---------------- Revenue ----------------
with tabs[2]:
    pay = (df[df["Payment_Method"] != "Not Applicable"]
           .groupby("Payment_Method")["Booking_Value"].sum().reset_index())
    left, right = st.columns(2)
    with left:
        show(px.bar(pay, x="Payment_Method", y="Booking_Value", text_auto=".3s",
                    title="Revenue by Payment Method"))
    top_cust = df.groupby("Customer_ID")["Booking_Value"].sum().nlargest(5).reset_index()
    with right:
        show(px.bar(top_cust, x="Customer_ID", y="Booking_Value", text_auto=".3s",
                    title="Top 5 Customers by Booking Value"))
    if not pay.empty:
        top_pay = pay.sort_values("Booking_Value").iloc[-1]
        insight(f"<b>{top_pay['Payment_Method']}</b> brings the most revenue "
                f"(₹{top_pay['Booking_Value']:,.0f}).")
    dist_day = df.groupby(df["Date"].dt.date)["Ride_Distance"].sum().reset_index()
    dist_day.columns = ["Date", "Total Distance"]
    show(px.bar(dist_day, x="Date", y="Total Distance", title="Ride Distance Per Day"), 240)


# ---------------- Cancellations ----------------
def reason_chart(column, title, color):
    reasons = df[column].dropna()
    reasons = reasons[reasons != "Not Applicable"]
    counts = reasons.value_counts().rename_axis("Reason").reset_index(name="Rides")
    if counts.empty:
        st.info(f"No data for: {title}")
        return
    fig = px.bar(counts, x="Rides", y="Reason", orientation="h", title=title, text_auto=True)
    fig.update_traces(marker_color=color)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    show(fig, 400)


with tabs[3]:
    left, right = st.columns(2)
    with left:
        reason_chart("Canceled_Rides_by_Customer", "Cancellation Reasons (Customer)", ORANGE)
    with right:
        reason_chart("Canceled_Rides_by_Driver", "Cancellation Reasons (Driver)", RED)

# ---------------- Ratings ----------------
with tabs[4]:
    left, right = st.columns(2)
    with left:
        fig = px.histogram(df.dropna(subset=["Driver_Ratings"]), x="Driver_Ratings", nbins=20,
                           title="Driver Ratings Distribution")
        fig.update_traces(marker_color=BLUE)
        show(fig)
    with right:
        fig = px.histogram(df.dropna(subset=["Customer_Rating"]), x="Customer_Rating", nbins=20,
                           title="Customer Ratings Distribution")
        fig.update_traces(marker_color=YELLOW)
        show(fig)
    both = (df.groupby("Vehicle_Type")[["Driver_Ratings", "Customer_Rating"]].mean().reset_index()
            .melt(id_vars="Vehicle_Type", var_name="Rating Type", value_name="Average Rating"))
    show(px.bar(both, x="Vehicle_Type", y="Average Rating", color="Rating Type", barmode="group",
                text_auto=".2f", title="Customer vs Driver Ratings",
                color_discrete_map={"Driver_Ratings": BLUE, "Customer_Rating": YELLOW}), 300)

# ---------------- SQL Explorer ----------------
QUERIES = {
    "1. Successful bookings": "SELECT * FROM ola_rides\nWHERE Booking_Status = 'Success';",
    "2. Average ride distance per vehicle type": "SELECT Vehicle_Type, AVG(Ride_Distance) AS avg_distance\nFROM ola_rides\nGROUP BY Vehicle_Type;",
    "3. Rides cancelled by customers": "SELECT COUNT(*) AS cancelled_by_customers\nFROM ola_rides\nWHERE Booking_Status = 'Canceled by Customer';",
    "4. Top 5 customers by number of rides": "SELECT Customer_ID, COUNT(*) AS total_rides\nFROM ola_rides\nGROUP BY Customer_ID\nORDER BY total_rides DESC\nLIMIT 5;",
    "5. Driver cancellations (personal and car issues)": "SELECT COUNT(*) AS driver_cancellations\nFROM ola_rides\nWHERE Canceled_Rides_by_Driver LIKE '%Personal%Car%';",
    "6. Max and min driver rating (Prime Sedan)": "SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating\nFROM ola_rides\nWHERE Vehicle_Type = 'Prime Sedan';",
    "7. Rides paid by UPI": "SELECT * FROM ola_rides\nWHERE Payment_Method = 'UPI';",
    "8. Average customer rating per vehicle type": "SELECT Vehicle_Type, AVG(Customer_Rating) AS avg_customer_rating\nFROM ola_rides\nGROUP BY Vehicle_Type;",
    "9. Total booking value of successful rides": "SELECT SUM(Booking_Value) AS total_booking_value\nFROM ola_rides\nWHERE Booking_Status = 'Success';",
    "10. Incomplete rides with reason": "SELECT Booking_ID, Incomplete_Rides_Reason\nFROM ola_rides\nWHERE Incomplete_Rides = 'Yes';",
}

with tabs[5]:
    left, right = st.columns([2, 3])
    choice = left.selectbox("Choose a SQL query (runs on the full dataset, filters above do not apply)", list(QUERIES))
    sql = QUERIES[choice]
    left.code(sql, language="sql")
    result = pd.read_sql_query(sql, make_sql_connection(csv_path))
    right.success(f"{len(result):,} rows returned")
    right.dataframe(result.head(1000), height=300)
    right.download_button("⬇️ Download result as CSV", result.to_csv(index=False), "query_result.csv", "text/csv")


# ---------------- Power BI ----------------
with tabs[6]:
    POWERBI_URL = ""
    if POWERBI_URL:
        components.iframe(POWERBI_URL, height=650)
    else:

        folder = Path(__file__).resolve().parent.parent / "Dashboard"
        images = sorted(list(folder.glob("*.png")) + list(folder.glob("*.jpg")))
        if images:
            st.caption("Power BI dashboard pages")
            for img in images:
                st.image(str(img), caption=img.stem)
        else:
            st.info("Add your Power BI page screenshots (.png) to the Dashboard folder.")

        st.info("Publish your Power BI report, then paste its link into POWERBI_URL at the top of app.py.")

