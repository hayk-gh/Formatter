import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import csv

def process_trend_report():
    input_file = input("Please type the name of your CSV file and press Enter: ").strip()
    
    if not os.path.exists(input_file):
        print(f"\nERROR: Could not find a file named '{input_file}' in this folder.")
        return

    print(f"Processing {input_file}...")

    # Find max columns to prevent errors
    max_cols = 0
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > max_cols:
                max_cols = len(row)

    # Load raw data
    df_raw = pd.read_csv(input_file, header=None, names=range(max_cols), dtype=str)
    num_cols = df_raw.shape[1]
    processed_blocks = []
    month_name = "Processed" 
    file_prefix = "" # Tracks whether the file is CP or BP for naming
    
    # Process in groups of 4 columns
    for start_col in range(0, num_cols, 4):
        if start_col >= num_cols or pd.isna(df_raw.iloc[7, start_col]) or 'timestamp' not in str(df_raw.iloc[7, start_col]).lower():
            continue
            
        # Identify if this block is CP or BP based on row 0 (Point Name)
        point_name_text = str(df_raw.iloc[0, start_col]).upper()
        if "CP-" in point_name_text or "COOLER" in point_name_text:
            plant_type = "CP"
            if not file_prefix:
                file_prefix = "CP_"
        else:
            plant_type = "BP" # Default fallback safely assumes BP if not explicit CP
            if not file_prefix:
                file_prefix = "BP_"

        cols_to_extract = [start_col, start_col + 1, start_col + 2]
        cols_to_extract = [c for c in cols_to_extract if c < num_cols]
        
        # Separate metadata from data
        metadata = df_raw.iloc[0:8, cols_to_extract].copy()
        data_block = df_raw.iloc[8:, cols_to_extract].copy()
        
        block_cols = ['TimeStamp', 'Value', 'Reliability']
        data_block.columns = block_cols[:len(cols_to_extract)]
        if 'Reliability' not in data_block.columns:
            data_block['Reliability'] = ""
        
        data_block = data_block.dropna(subset=['TimeStamp'])
        
        # Parse dates
        data_block['TimeStamp'] = pd.to_datetime(data_block['TimeStamp'], format='mixed', errors='coerce')
        data_block = data_block.dropna(subset=['TimeStamp'])
        
        if data_block.empty:
            continue

        # Round to nearest hour and deduplicate
        data_block['RoundedTime'] = data_block['TimeStamp'].dt.round('h')
        data_block['Diff'] = (data_block['TimeStamp'] - data_block['RoundedTime']).abs()
        
        data_block = data_block.sort_values(['RoundedTime', 'Diff'])
        data_block = data_block.drop_duplicates(subset=['RoundedTime'], keep='first')
        
        # Get month bounds
        t = data_block['TimeStamp'].iloc[0]
        month_name = t.strftime('%B') 
        
        start_date = datetime(t.year, t.month, 1, 0, 0)
        if t.month == 12:
            end_date = datetime(t.year + 1, 1, 1) - timedelta(hours=1)
        else:
            end_date = datetime(t.year, t.month + 1, 1) - timedelta(hours=1)
            
        # Create full month timeline
        full_range = pd.date_range(start=start_date, end=end_date, freq='h')
        month_df = pd.DataFrame({'RoundedTime': full_range})
        
        # Merge data onto timeline
        final_block = pd.merge(month_df, data_block, on='RoundedTime', how='left')
        
        # Fill missing hours
        missing_mask = final_block['Value'].isna()
        final_block.loc[missing_mask, 'Value'] = '0'
        final_block.loc[missing_mask, 'Reliability'] = '?'
        
        final_block['TimeStampStr'] = final_block['RoundedTime'].dt.strftime('%#m/%#d/%Y %H:00')
        out_data = final_block[['TimeStampStr', 'Value', 'Reliability']].copy()
        
        # Calculate sum raw math numbers
        numeric_values = pd.to_numeric(out_data['Value'].str.replace(',', ''), errors='coerce').fillna(0)
        total_sum_num = numeric_values.sum()
        total_sum_str = f"{int(total_sum_num):,}"
        sum_row = pd.DataFrame([['Total Sum', total_sum_str, '']], columns=out_data.columns)
        
        # Calculate plant conditional MMBtuh math row
        if plant_type == "CP":
            mmbtuh_label = "CP MMBtuh"
            mmbtuh_calc = total_sum_num / 1000
        else:
            mmbtuh_label = "BP MMBtuh"
            mmbtuh_calc = total_sum_num * 0.012
            
        mmbtuh_str = f"{mmbtuh_calc:,.3f}" # Formats cleanly with commas and 3 decimal places
        mmbtuh_row = pd.DataFrame([[mmbtuh_label, mmbtuh_str, '']], columns=out_data.columns)
        
        # Rebuild block with metadata, sum row, and MMBtuh row
        meta_df = pd.DataFrame(metadata.values, columns=out_data.columns)
        full_processed_block = pd.concat([meta_df, out_data, sum_row, mmbtuh_row], ignore_index=True)
        
        if start_col + 3 < num_cols:
            full_processed_block['Spacer'] = ""
        processed_blocks.append(full_processed_block)

    if not processed_blocks:
        print("\nERROR: No valid data blocks could be parsed from this file.")
        return

    # Combine blocks and save
    final_output = pd.concat(processed_blocks, axis=1)
    
    current_time = time.strftime("%Y%m%d_%H%M")
    
    # Prepend CP_ or BP_ to the beginning of the file name string securely
    if not file_prefix:
        file_prefix = "Processed_"
    base_filename = f"{file_prefix}{month_name}_Report_{current_time}"
    
    final_output.to_csv(f"{base_filename}.csv", index=False, header=False)
    final_output.to_excel(f"{base_filename}.xlsx", index=False, header=False)

    print(f"\nSUCCESS! Created your reports:")
    print(f" - {base_filename}") 
    print(f" (Available in both Excel and CSV formats)")

if __name__ == "__main__":
    try:
        process_trend_report()
    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")
    
    input("\nProcessing complete. Press Enter to close this window...")