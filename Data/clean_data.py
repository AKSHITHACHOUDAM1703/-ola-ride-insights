import pandas as pd

# 1. Read the original Excel dataset
df = pd.read_excel("Data/OLA_DataSet.xlsx")

# 2. Remove extra spaces from text values safely
text_columns = df.select_dtypes(include=["object", "string"]).columns

for column in text_columns:
    df[column] = df[column].map(
        lambda value: value.strip() if isinstance(value, str) else value
    )

# 3. Convert the Time column to time format
df["Time"] = pd.to_datetime(
    df["Time"].astype(str),
    errors="coerce"
).dt.time

# 4. Create new columns useful for analysis
df["Hour"] = pd.to_datetime(
    df["Time"].astype(str),
    errors="coerce"
).dt.hour

df["Day_Name"] = df["Date"].dt.day_name()
df["Month"] = df["Date"].dt.month_name()
df["Day_Number"] = df["Date"].dt.day

# 5. Fill missing cancellation/incomplete reasons
reason_columns = [
    "Canceled_Rides_by_Customer",
    "Canceled_Rides_by_Driver",
    "Incomplete_Rides",
    "Incomplete_Rides_Reason"
]

for column in reason_columns:
    df[column] = df[column].fillna("Not Applicable")

# Keep missing values for ratings, distance, V_TAT, and C_TAT.
# These may be naturally blank for cancelled or incomplete rides.

# 6. Save cleaned data as a CSV file
df.to_csv("Data/ola_cleaned.csv", index=False)

# 7. Show confirmation
print("Cleaning complete!")
print("Cleaned file saved as: Data/ola_cleaned.csv")
print("Rows:", len(df))
print("Columns:", len(df.columns))