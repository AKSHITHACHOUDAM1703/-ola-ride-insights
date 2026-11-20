# OLA Ride Insights

Analysis of OLA ride-sharing data using **Python, MySQL, Power BI and Streamlit**.
The project cleans the raw data, answers 10 business questions with SQL, presents a 5-page Power BI dashboard and shares an interactive Streamlit web app.

| | |
|---|---|
| **Live app** | https://r8bkhngvjwdkxapdcerhyx.streamlit.app/ |
| **GitHub** | https://github.com/AKSHITHACHOUDAM1703/-ola-ride-insights |
| 
| **Author** | CH. AKSHITHA |
| **Date** | 20-11-2026 |

---

## Key Numbers (July 2024)

| Metric | Value |
|---|---|
| Total bookings | 103,024 |
| Revenue (successful rides) | ₹35,080,467 |
| Success rate | 62.1% (63,967 rides) |
| Cancelled by driver | 17.9% (18,434) |
| Cancelled by customer | 10.2% (10,499) |
| Driver Not Found | 9.8% (10,124) |
| Daily rides | 3,072 to 3,432 (average 3,323) |
| Cash / UPI / cards share of revenue | 54.9% / 40.4% / 4.7% |

## Key Insights

- Only **62.1%** of bookings are completed. About **₹21.45M** of booking value was lost to cancellations and bookings with no driver found.
- **Driver cancellations:** personal and car-related issues are the top reason (6,542, 35.5%).
- **Customer cancellations:** 55.7% are driver-related (driver not moving towards pickup, or driver asked to cancel).
- **Demand is steady** through the day and week. The busiest hour (12:00) is less than 6% above the quietest (18:00).
- **Auto** rides average 10 km; all other vehicle types average about 25 km.
- **6.1%** of successful rides were incomplete, mostly because of customer demand or vehicle breakdown.

---

## Project Components

| Component | Description |
|---|---|
| Data preparation | Python scripts (Pandas) that check, clean and save the dataset. Cleaned file: `Data/ola_cleaned.csv` |
| SQL analysis | 10 MySQL queries in `SQL/OLA_SQL_Queries.sql` |
| Power BI dashboard | 5-page dashboard in the `Dashboard` folder |
| Streamlit app | Interactive dashboard in `app/app.py` |

## Repository Structure

```
-ola-ride-insights/
  Dashboard/        Dashboard page images and the .pbix file
  Data/             OLA_DataSet.xlsx, ola_cleaned.csv and the Python scripts
  SQL/              OLA_SQL_Queries.sql
  app/app.py        Streamlit app
  requirements.txt
  README.md
```

## Data Cleaning Steps

1. Read the original Excel dataset (`OLA_DataSet.xlsx`).
2. Removed extra spaces from text columns.
3. Converted the Time column to a proper time format.
4. Created new columns: `Hour`, `Day_Name`, `Month` and `Day_Number`.
5. Filled blank cancellation and incomplete-ride reasons with "Not Applicable".
6. Kept blank ratings and turnaround times for cancelled rides (they are naturally empty).
7. Saved the result as `Data/ola_cleaned.csv` (103,024 rows, 24 columns).

Quality checks: no duplicate rows or Booking_IDs, consistent categories, and ratings between 3.0 and 5.0.

## SQL Questions Answered

| # | Question | Result |
|---|---|---|
| 1 | All successful bookings | 63,967 rows |
| 2 | Average ride distance per vehicle type (successful rides) | Auto 10.04 km; others about 25 km |
| 3 | Rides cancelled by customers | 10,499 |
| 4 | Top 5 customers by number of rides | CID954071 (5 rides) and four customers with 4 rides |
| 5 | Driver cancellations: personal and car-related issues | 6,542 |
| 6 | Max and min driver rating for Prime Sedan | 5.0 and 3.0 |
| 7 | Rides paid by UPI | 25,881 |
| 8 | Average customer rating per vehicle type | 3.988 to 4.009 |
| 9 | Total booking value of successful rides | ₹35,080,467 |
| 10 | Incomplete rides with reason | 3,926 rides |

## Power BI Dashboard

### 1. Overall
Ride volume over time, booking status breakdown, KPI cards and slicers.

![Overall](Dashboard/1.Overall.png)

### 2. Vehicle Type
Top 5 vehicle types by ride distance.

![Vehicle Type](Dashboard/2.Vehicle_Type.png)

### 3. Revenue
Revenue by payment method, top 5 customers by booking value, ride distance per day.

![Revenue](Dashboard/3.Revenue.png)

### 4. Cancellation
Cancellation reasons for customers and drivers.

![Cancellation](Dashboard/4.Cancellation.png)

### 5. Ratings
Driver ratings distribution, customer ratings by vehicle type, customer vs driver ratings.

![Ratings](Dashboard/5.Ratings.png)

## Streamlit App

**Live app:** https://r8bkhngvjwdkxapdcerhyx.streamlit.app/

- Click-to-select filters for booking status, vehicle type and payment method, plus a date range, an ID search and a reset button
- KPI cards: total rides, revenue, average distance, success rate and cancellation rate
- Tabs: Overview, Vehicles, Revenue, Cancellations, Ratings, SQL Explorer and Power BI
- Peak-hours chart and a day-versus-hour demand heatmap
- SQL Explorer: run the 10 project queries and download the results as CSV

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Tech Stack

Python, Pandas, Plotly, Streamlit, MySQL, SQLAlchemy, Power BI, GitHub

## Notes

- Revenue means the booking value of **successful rides only** (₹35,080,467). All bookings together total ₹56,534,614, but the rest was never earned.
- The 28.1% cancellation rate counts customer and driver cancellations. Including Driver Not Found, 37.9% of bookings were not completed.
- The data covers one month (July 2024).
