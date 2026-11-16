import pandas as pd
from getpass import getpass
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Read the cleaned OLA dataset
df = pd.read_csv("Data/ola_cleaned.csv")

# Enter MySQL password safely when the program runs
mysql_password = input("Enter ola_user MySQL password: ")
# Create a safe MySQL connection
connection_url = URL.create(
    drivername="mysql+pymysql",
    username="ola_user",
    password=mysql_password,
    host="localhost",
    port=3306,
    database="ola_ride_project"
)

engine = create_engine(connection_url)

# Create the ola_rides table and import all rows
df.to_sql(
    name="ola_rides",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=500,
    method="multi"
)

print("Import complete!")
print("Table name: ola_rides")
print("Rows imported:", len(df))