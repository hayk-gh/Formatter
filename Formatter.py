import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os

def process_trend_report():
    input_file = input("Please type the name of your CSV file and press Enter: ").strip()
    
    if not os.path.exists(input_file):
        print(f"\nERROR: Could not find a file named '{input_file}' in this folder.")
        return

    print(f"Processing {input_file}...")

    df_raw = pd.read_csv(input_file, header=None, dtype=str)
    num_cols = df_raw.shape[1]
    processed_blocks = []
    month_name = "Processed" 
    
    for start_col in range(0, num_cols, 4):
        cols_to_extract = [start_col, start_col + 1, start_col + 2]
        cols_to_extract = [c for c in cols_to_extract if c < num_cols]
        
        if not cols_to_extract:
            continue
            
        metadata = df_raw.iloc[0:8, cols_to_extract].copy()
        data_block = df_raw.iloc[8:, cols_to_extract].copy()
        data_block.columns = ['TimeStamp', 'Value', 'Reliability']
        
        data_block = data_block.dropna(subset=['TimeStamp'])
        data_block['TimeStamp'] = pd.to_datetime(data_block['TimeStamp'])
        data_block['RoundedTime'] = data_block['TimeStamp'].dt.round('h')
        data_block['Diff'] = (data_block['TimeStamp'] - data_block['RoundedTime']).abs()
        
        data_block = data_block.sort_values(['RoundedTime', 'Diff'])
        data_block = data_block.drop_duplicates(subset=['RoundedTime'], keep='first')
        
        t = data_block['TimeStamp'].iloc[0]
        month_name = t.strftime('%B') 
        
        start_date = datetime(t.year, t.month, 1, 0, 0)
        if t.month == 12:
            end_date = datetime(t.year + 1, 1, 1) - timedelta(hours=1)
        else:
            end_date = datetime(t.year, t.month + 1, 1) - timedelta(hours=1)
            
        full_range = pd.date_range(start=start_date, end=end_date, freq='h')
        month_df = pd.DataFrame({'RoundedTime': full_range})
        
        final_block = pd.merge(month_df, data_block, on='RoundedTime', how='left')
        
        missing_mask = final_block['Value'].isna()
        final_block.loc[missing_mask, 'Value'] = '0'
        final_block.loc[missing_mask, 'Reliability'] = '?'
        
        final_block['TimeStampStr'] = final_block['RoundedTime'].dt.strftime('%#m/%#d/%Y %H:00')
        
        out_data = final_block[['TimeStampStr', 'Value', 'Reliability']].copy()
        meta_df = pd.DataFrame(metadata.values, columns=out_data.columns)
        full_processed_block = pd.concat([meta_df, out_data], ignore_index=True)
        
        if start_col + 3 < num_cols:
            full_processed_block['Spacer'] = ""
        processed_blocks.append(full_processed_block)

    final_output = pd.concat(processed_blocks, axis=1)
    
    # 1. Create a clean base name (The "First Name")
    current_time = time.strftime("%Y%m%d_%H%M")
    base_filename = f"{month_name}_Report_{current_time}"
    
    # 2. Save the files (Adding the "ID Tag" so they work)
    final_output.to_csv(f"{base_filename}.csv", index=False, header=False)
    final_output.to_excel(f"{base_filename}.xlsx", index=False, header=False)

    # 3. Clean console output
    print(f"\nSUCCESS! Created your reports:")
    print(f" - {base_filename}") 
    print(f" (Available in both Excel and CSV formats)")

if __name__ == "__main__":
    try:
        process_trend_report()
    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")
    
    input("\nProcessing complete. Press Enter to close this window...")