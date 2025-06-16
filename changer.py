import pandas as pd
import re

class FlightDataProcessor:
    def __init__(self, original_file, new_format_file):
        self.df_original = pd.read_csv("flight_data\Cleaned_dataset.csv")
        self.df_new_format = pd.read_csv("flight_data\cleaned_file.csv")
        
    def clean_new_format_data(self):
        # Map columns from new format to original format
        column_mapping = {
            'flight_date': 'Date_of_journey',
            'airline': 'Airline',
            'flight_num': 'Flight_code',
            'class': 'Class',
            'from_city': 'Source',
            'dep_time': 'Departure',
            'to_city': 'Destination',
            'arr_time': 'Arrival',
            'duration': 'Duration_in_hours',
            'stops': 'Total_stops',
            'price': 'Fare'
        }
        
        # Keep only columns that exist in the original format
        original_columns = ['Date_of_journey', 'Airline', 'Flight_code', 'Class', 
                          'Source', 'Departure', 'Destination', 'Arrival', 
                          'Duration_in_hours', 'Fare', 'Total_stops']
        
        # Rename and select columns in the new format dataframe
        self.df_new_format = self.df_new_format.rename(columns=column_mapping)
        self.df_new_format = self.df_new_format[[col for col in original_columns if col in self.df_new_format.columns]]
        
        # Clean departure time in the new format data
        def parse_time(time_str):
            if pd.isna(time_str):
                return "00:00"
            
            time_str = str(time_str).lower()
            
            # Handle approximate times
            if "after" in time_str:
                if "6 pm" in time_str:
                    return "18:30"
                elif "12 pm" in time_str:
                    return "12:30"
                elif "6 am" in time_str:
                    return "06:30"
            elif "before" in time_str:
                if "6 am" in time_str:
                    return "05:30"
                elif "6 pm" in time_str:
                    return "17:30"
                elif "12 pm" in time_str:
                    return "11:30"
            
            # Handle time ranges
            if "-" in time_str:
                times = time_str.split("-")
                start_time = times[0].strip()
                if "am" in start_time or "pm" in start_time:
                    hour = re.search(r'(\d+)', start_time).group(1)
                    period = "AM" if "am" in start_time else "PM"
                    return f"{int(hour):02d}:00" if period == "AM" else f"{int(hour)+12 if int(hour) < 12 else int(hour):02d}:00"
            
            # Default case for exact times
            return time_str
        
        self.df_new_format['Departure'] = self.df_new_format['Departure'].apply(parse_time)
        
        # Standardize class categories
        self.df_new_format['Class'] = self.df_new_format['Class'].str.lower()
        class_mapping = {
            'economy': 'Economy',
            'business': 'Business',
            'premium economy': 'Economy',  # Map premium economy to economy
            'primum economy': 'Economy'     # Handle typo
        }
        self.df_new_format['Class'] = self.df_new_format['Class'].map(class_mapping).fillna('Economy')
        
        # Convert duration to consistent format (original uses hours as float)
        def convert_duration(duration):
            if isinstance(duration, float) or isinstance(duration, int):
                hours = int(duration)
                mins = int((duration - hours) * 60)
                return f"{hours:02d}h {mins:02d}m"
            elif isinstance(duration, str):
                if 'h' in duration and 'm' in duration:
                    return duration
                try:
                    hours = float(duration)
                    mins = int((hours - int(hours)) * 60)
                    return f"{int(hours):02d}h {mins:02d}m"
                except:
                    return "00h 00m"
            return "00h 00m"
        
        self.df_new_format['Duration_in_hours'] = self.df_new_format['Duration_in_hours'].apply(convert_duration)
        
        # Clean price formatting (remove commas)
        if 'Fare' in self.df_new_format.columns:
            self.df_new_format['Fare'] = self.df_new_format['Fare'].astype(str).str.replace(',', '').astype(float)
        
    def merge_datasets(self):
        # Concatenate both dataframes
        merged_df = pd.concat([self.df_original, self.df_new_format], ignore_index=True)
        
        # Remove duplicates based on flight number
        merged_df = merged_df.drop_duplicates(subset=['Flight_code'], keep='first')
        
        return merged_df
    
    def process_and_save(self):
        self.clean_new_format_data()
        merged_data = self.merge_datasets()
        
        # Save to final file
        final_filename = 'final_flight_data.csv'
        merged_data.to_csv(final_filename, index=False)
        
        print(f"Data processing complete. Final merged data saved to {final_filename}")
        return merged_data

# Usage
processor = FlightDataProcessor('flight_data_new_format.csv', 'flight_data.csv')
final_data = processor.process_and_save()