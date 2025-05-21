import pandas as pd
import re
import os

# Folder containing your Excel files
folder_path = os.path.dirname(os.path.abspath(__file__))  # Current directory of the script

# Function to clean phone numbers
# Define phone cleaning function
def clean_phone(number):
    if pd.isna(number):
        return None
        
    # Remove non-digits
    digits = re.sub(r'\D', '', str(number))
        
    # Handle different formats
    if len(digits) == 0:
        return None
    elif digits.startswith('84'):
        return '+' + digits
    else:
        # Remove leading zero if present
        return '+84' + digits.lstrip('0')


# Loop through all Excel files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".xlsx"):
        file_path = os.path.join(folder_path, filename)

        # Load the file
        df = pd.read_excel(file_path)
        # Check if the file is empty
        if df.empty:
            print(f"Skipped (empty file): {filename}")
            continue
        
        # Try to guess the phone number column name
        phone_col = None
        possible_phone_columns = ['DIEN THOAI', 'Số điện thoại', 'SĐT', 'SDT', 'phone', 'Điện thoại', 'PHONE']
        
        # Check for common phone number column names
        for col in possible_phone_columns:
            if col in df.columns:
                phone_col = col
                break
       
        # If no common column name found, try to find a column with phone-like data
        if phone_col is None:
            print(f"Error: No phone column found. Available columns are: {list(df.columns)}")
            exit(1)

        # If a phone column is found, clean the phone numbers
        if phone_col:
            df['Cleaned_Phone'] = df[phone_col].apply(clean_phone)

            # Save to a new file (or overwrite)
            output_path = os.path.join(folder_path, f"cleaned_{filename}")
            df.to_excel(output_path, index=False)
            print(f"Processed: {filename}")
        else:
            print(f"Skipped (no phone column found): {filename}")
