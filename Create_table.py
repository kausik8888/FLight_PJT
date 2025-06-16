import pandas as pd
from mysql_connect_safe import connet_to_mysql

# === STEP 1: Load & Preprocess CSV ===

# Use raw string to avoid backslash escape issues
df = pd.read_csv(r"flight_data\final_cleaned_flight_data.csv")

# Convert flight_date, dep_time, arr_time
df['flight_date'] = pd.to_datetime(df['flight_date'], format='%d-%m-%Y', errors='coerce').dt.date
df['dep_time'] = pd.to_datetime(df['dep_time'], format='%H:%M', errors='coerce').dt.time
df['arr_time'] = pd.to_datetime(df['arr_time'], format='%H:%M', errors='coerce').dt.time

# Clean price column (remove commas, convert to float)
df['price'] = df['price'].astype(str).str.replace(',', '', regex=True).astype(float)

# Convert all NaN to None (MySQL accepts None as NULL)
data = [
    tuple(None if pd.isna(val) else val for val in row)
    for row in df.itertuples(index=False, name=None)
]

# === STEP 2: Server Class for DB Handling ===

class Server:
    def __init__(self, data):
        self.data = data

    def run_query(self):
        connection = connet_to_mysql()
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = """
                    CREATE TABLE IF NOT EXISTS all_data (
                        flight_date DATE,
                        airline VARCHAR(100),
                        flight_num VARCHAR(100),
                        class VARCHAR(100),
                        from_city VARCHAR(100),
                        dep_time TIME,
                        to_city VARCHAR(100),
                        arr_time TIME,
                        duration VARCHAR(100),
                        price DECIMAL(10,2),
                        stops VARCHAR(50)
                    );
                    """
                    cursor.execute(query)
                    connection.commit()
                    print("Table created successfully.")
            except Exception as e:
                print(f"Error during table creation: {e}")
            finally:
                connection.close()
        else:
            print("Failed to connect to database.")

    def insert_dquery(self):
        connection = connet_to_mysql()
        if connection:
            try:
                with connection.cursor() as cursor:
                    insert_query = """
                    INSERT INTO all_data (
                        flight_date, airline, flight_num, class, from_city, dep_time,
                        to_city, arr_time, duration, price, stops
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                    """
                    cursor.executemany(insert_query, self.data)
                    connection.commit()
                    print(f"{cursor.rowcount} rows inserted successfully.")
            except Exception as e:
                print(f"Error during data insertion: {e}")
            finally:
                connection.close()
        else:
            print("Failed to connect to database.")

# === STEP 3: Run All ===

if __name__ == "__main__":
    s = Server(data)
    s.run_query()
    s.insert_dquery()

