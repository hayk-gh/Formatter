import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os

def process_trend_report():
    # This replaces the hardcoded name. It asks the user to type it instead.
    input_file = input("Please type the name of your CSV file and press Enter: ").strip()
    
    # Check if the file actually exists so the program doesn't just crash
    if not os.path.exists(input_file):
        print(f"\nERROR: Could not find a file named '{input_file}' in this folder.")
        input("Press Enter to close...")
        return

    # Load the file as text to avoid formatting errors
    df_raw = pd.read_csv(input_file, header=None, dtype=str)
    
    num_cols = df_raw.shape[1]
    processed_blocks = []
    month_name = "Processed" 
    
    # Process the file in groups of 4 columns
    for start_col in range(0, num_cols, 4):
        cols_to_extract = [start_col, start_col + 1, start_col + 2]
        cols_to_extract = [c for c in cols_to_extract if c < num_cols]
        
        if not cols_to_extract:
            continue
            
        # Separate the top 8 rows (headers) from the actual data
        metadata = df_raw.iloc[0:8, cols_to_extract].copy()
        data_block = df_raw.iloc[8:, cols_to_extract].copy()
        data_block.columns = ['TimeStamp', 'Value', 'Reliability']
        
        # Convert text into readable dates and times
        data_block = data_block.dropna(subset=['TimeStamp'])
        data_block['TimeStamp'] = pd.to_datetime(data_block['TimeStamp'])
        
        # Round every entry to the nearest hour
        data_block['RoundedTime'] = data_block['TimeStamp'].dt.round('h')
        
        # Calculate how far each entry is from the exact hour
        data_block['Diff'] = (data_block['TimeStamp'] - data_block['RoundedTime']).abs()
        
        # Pick the most accurate entry for each hour and remove duplicates
        data_block = data_block.sort_values(['RoundedTime', 'Diff'])
        data_block = data_block.drop_duplicates(subset=['RoundedTime'], keep='first')
        
        # Identify the month and create a list of every hour for the entire month
        t = data_block['TimeStamp'].iloc[0]
        target_month = t.month
        target_year = t.year
        month_name = t.strftime('%B') 
        
        start_date = datetime(target_year, target_month, 1, 0, 0)
        if target_month == 12:
            end_date = datetime(target_year + 1, 1, 1) - timedelta(hours=1)
        else:
            end_date = datetime(target_year, target_month + 1, 1) - timedelta(hours=1)
            
        full_range = pd.date_range(start=start_date, end=end_date, freq='h')
        month_df = pd.DataFrame({'RoundedTime': full_range})
        
        # Match the existing data with the new hourly list
        final_block = pd.merge(month_df, data_block, on='RoundedTime', how='left')
        
        # If an hour is missing, set value to 0 and reliability to '?'
        missing_mask = final_block['Value'].isna()
        final_block.loc[missing_mask, 'Value'] = '0'
        final_block.loc[missing_mask, 'Reliability'] = '?'
        
        # Format times to standard xx:00
        final_block['TimeStampStr'] = final_block['RoundedTime'].dt.strftime('%#m/%#d/%Y %H:00')
        
        # Put the headers and the new data back together
        out_data = final_block[['TimeStampStr', 'Value', 'Reliability']].copy()
        meta_df = pd.DataFrame(metadata.values, columns=out_data.columns)
        full_processed_block = pd.concat([meta_df, out_data], ignore_index=True)
        
        # Add a spacer column between data groups
        if start_col + 3 < num_cols:
            full_processed_block['Spacer'] = ""
            
        processed_blocks.append(full_processed_block)

    # Combine everything and save the file with the month and a timestamp
    final_output = pd.concat(processed_blocks, axis=1)
    current_time = time.strftime("%Y%m%d_%H%M")
    output_file = f"{month_name}_Processed_Report_{current_time}.csv"
    
    final_output.to_csv(output_file, index=False, header=False)
    print(f"\nSUCCESS! File saved as: {output_file}")
    input("\nPress Enter to close this window...")

if __name__ == "__main__":
    process_trend_report()