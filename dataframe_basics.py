import pandas as pd
import pymysql as db
from mysql_connect_safe import connet_to_mysql()
# Load the dataset
df=pd.read_csv("flight_data\goibibo_flights_data.csv")
# Drop completely empty columns if they exist
df = df.dropna(axis=1, how='all')

unique_flight_routes = df[['flight_num', 'from', 'to']].drop_duplicates()
unique_flight_routes.to_csv("unique_flight_num.csv",index=False)




