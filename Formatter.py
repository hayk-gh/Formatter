import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import csv

def process_trend_report():
    # Get the source filename from the user
    input_file = input("Please type the name of your CSV file and press Enter: ").strip()
    
    if not os.path.exists(input_file):
        print(f"\nERROR: Could not find a file named '{input_file}' in this folder.")
        return

    print(f"Processing {input_file}...")

    # Pre-scan the file to find the maximum number of columns (prevents tokenization errors)
    max_cols = 0
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > max_cols:
                max_cols = len(row)

    # Load the raw file data using the maximum column layout
    df_raw = pd.read_csv(input_file, header=None, names=range(max_cols), dtype=str)
    num_cols = df_raw.shape[1]
    processed_blocks = []
    month_name = "Processed" 
    
    # Process the data grid in chunks of 4 columns
    for start_col in range(0, num_cols, 4):
        # Skip empty spacer blocks or non-data streams
        if start_col >= num_cols or pd.isna(df_raw.iloc[7, start_col]) or 'timestamp' not in str(df_raw.iloc[7, start_col]).lower():
            continue
            
        cols_to_extract = [start_col, start_col + 1, start_col + 2]
        cols_to_extract = [c for c in cols_to_extract if c < num_cols]
        
        # Isolate the top 8 metadata header rows from the underlying time series data
        metadata = df_raw.iloc[0:8, cols_to_extract].copy()
        data_block = df_raw.iloc[8:, cols_to_extract].copy()
        
        block_cols = ['TimeStamp', 'Value', 'Reliability']
        data_block.columns = block_cols[:len(cols_to_extract)]
        if 'Reliability' not in data_block.columns:
            data_block['Reliability'] = ""
        
        data_block = data_block.dropna(subset=['TimeStamp'])
        
        # Dynamic date string handling for mixed formats (e.g., m/d/yyyy and Month d, Year)
        data_block['TimeStamp'] = pd.to_datetime(data_block['TimeStamp'], format='mixed', errors='coerce')
        data_block = data_block.dropna(subset=['TimeStamp'])
        
        if data_block.empty:
            continue

        # Round timestamps to the nearest hour and pick the entry closest to the exact hour mark
        data_block['RoundedTime'] = data_block['TimeStamp'].dt.round('h')
        data_block['Diff'] = (data_block['TimeStamp'] - data_block['RoundedTime']).abs()
        
        data_block = data_block.sort_values(['RoundedTime', 'Diff'])
        data_block = data_block.drop_duplicates(subset=['RoundedTime'], keep='first')
        
        # Determine target month boundaries using the first valid timestamp row
        t = data_block['TimeStamp'].iloc[0]
        month_name = t.strftime('%B') 
        
        start_date = datetime(t.year, t.month, 1, 0, 0)
        if t.month == 12:
            end_date = datetime(t.year + 1, 1, 1) - timedelta(hours=1)
        else:
            end_date = datetime(t.year, t.month + 1, 1) - timedelta(hours=1)
            
        # Build a complete chronological 1-hour timeline map for the entire month
        full_range = pd.date_range(start=start_date, end=end_date, freq='h')
        month_df = pd.DataFrame({'RoundedTime': full_range})
        
        # Merge raw data onto the timeline map to spot gaps
        final_block = pd.merge(month_df, data_block, on='RoundedTime', how='left')
        
        # Backfill any missing timeline hours with 0 value and a '?' reliability flag
        missing_mask = final_block['Value'].isna()
        final_block.loc[missing_mask, 'Value'] = '0'
        final_block.loc[missing_mask, 'Reliability'] = '?'
        
        final_block['TimeStampStr'] = final_block['RoundedTime'].dt.strftime('%#m/%#d/%Y %H:00')
        
        # Reconstruct the block by stitching the original top metadata headers back over the normalized data
        out_data = final_block[['TimeStampStr', 'Value', 'Reliability']].copy()
        meta_df = pd.DataFrame(metadata.values, columns=out_data.columns)
        full_processed_block = pd.concat([meta_df, out_data], ignore_index=True)
        
        # Append an empty spacer column tracking to isolate column clusters
        if start_col + 3 < num_cols:
            full_processed_block['Spacer'] = ""
        processed_blocks.append(full_processed_block)

    if not processed_blocks:
        print("\nERROR: No valid data blocks could be parsed from this file.")
        return

    # Combine all processed column blocks sideways into a single wide data frame
    final_output = pd.concat(processed_blocks, axis=1)
    
    current_time = time.strftime("%Y%m%d_%H%M")
    base_filename = f"{month_name}_Report_{current_time}"
    
    # Save the synchronized data output into both formats
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
    
    # Hold the terminal instance open for desktop execution runs
    input("\nProcessing complete. Press Enter to close this window...")