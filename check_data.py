import pandas as pd

file_path = "Data/OLA_DataSet.xlsx"

df = pd.read_excel(file_path)

print("\nFirst 5 rows:")
print(df.head())

print("\nColumn names:")
print(df.columns.tolist())

print("\nData information:")
print(df.info())

print("\nMissing values:")
print(df.isnull().sum())