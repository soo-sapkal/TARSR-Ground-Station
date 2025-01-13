import pandas as pd

try:
    df = pd.read_csv('sensor_data.csv')
    print(df.head())  # Print the first few rows of data
except pd.errors.EmptyDataError:
    print("The file is empty or invalid!")
