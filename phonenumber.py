import pandas as pd
import re
import os

folder_path = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(folder_path, 'output')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Define phone cleaning function (outside the loop to define it only once)
def clean_phone(number):
    if pd.isna(number):
        return None
    
    # Convert to string if not already
    number_str = str(number)
    
    # Check if there are multiple numbers separated by '-'
    if '-' in number_str and any(len(re.sub(r'\D', '', part)) >= 9 for part in number_str.split('-')):
        # Process each part separately while keeping the '-' separator
        parts = number_str.split('-')
        cleaned_parts = []
        for part in parts:
            digits_only = re.sub(r'\D', '', part)
            if len(digits_only) >= 9:  # Only format valid-length numbers
                if digits_only.startswith('84'):
                    cleaned_parts.append('+' + digits_only)
                else:
                    cleaned_parts.append('+84' + digits_only.lstrip('0'))
            else:
                cleaned_parts.append(part.strip())  # Keep as is if too short
        
        return ' - '.join(cleaned_parts)
    
    # Extract any parentheses content to preserve
    parentheses_match = re.search(r'(\([^)]*\))', number_str)
    parentheses_text = parentheses_match.group(1) if parentheses_match else ''
    
    # Remove parentheses content from the string before digit extraction
    if parentheses_text:
        number_str = number_str.replace(parentheses_text, '')
    
    # Extract only digits for the phone number part
    digits = re.sub(r'\D', '', number_str)
    
    # Check if phone number has enough digits (Vietnamese numbers typically have 10-11 digits)
    if len(digits) < 9:
        return f"WARNING"
    
    # Format the phone number
    if digits.startswith('84'):
        result = '+' + digits
    else:
        result = '+84' + digits.lstrip('0')
    
    # Add back any parentheses content
    if parentheses_text:
        result += ' ' + parentheses_text
    
    return result

for filename in os.listdir(folder_path):
    if filename.endswith(".xlsx"):
        file_path = os.path.join(folder_path, filename)
        try:
            print(f"Processing {filename}...")
            
            # Try different header rows (0 = first row, 1 = second row, etc.)
            found_header = False
            header_row = None
            
            # First read the file with header=None to get all rows
            all_data_df = pd.read_excel(file_path, engine='openpyxl', header=None)
            
            for test_row in range(0, 10):  # Try rows 0-9 (first 10 rows)
                try:
                    # Attempt to read with this header row
                    df = pd.read_excel(file_path, engine='openpyxl', header=test_row)
                    
                    # Check if the Phone column exists
                    phone_column = None
                    possible_phone_columns = ['DIEN THOAI', 'Số điện thoại', 'SĐT', 'SDT', 'phone', 
                                             'Điện thoại', 'PHONE', 'Phone', 'Mobile']
                    
                    for col in possible_phone_columns:
                        if col in df.columns:
                            phone_column = col
                            found_header = True
                            header_row = test_row
                            break
                    
                    if found_header:
                        print(f"  Found header at row {test_row+1} with column '{phone_column}'")
                        break
                        
                except Exception as e:
                    print(f"  Error reading header row {test_row}: {str(e)}")
                    continue  # Try next header row
            
            if not found_header:
                print(f"  Error: No valid header with phone column found in {filename}. Available columns in first row: {list(pd.read_excel(file_path, engine='openpyxl', header=0).columns)}")
                continue
            
            # Create a complete dataframe with all rows preserved
            if header_row > 0:
                # If header is not in first row, we need to preserve the rows above the header
                
                # Get the header row as column names
                column_names = list(df.columns)
                
                # Create a new dataframe with the header row data plus all rows
                result_df = pd.DataFrame(columns=column_names)
                
                # Add the rows above the header (with proper column alignment)
                for i in range(header_row):
                    new_row = pd.Series(all_data_df.iloc[i].values, index=column_names)
                    result_df = pd.concat([result_df, new_row.to_frame().T], ignore_index=True)
                
                # Add all the data rows from the correctly parsed dataframe
                result_df = pd.concat([result_df, df], ignore_index=True)
                
                # Now work with the complete dataframe that includes rows above the header
                df = result_df
            
            # Apply cleaning function
            df['Cleaned_Phone'] = df[phone_column].apply(clean_phone)
            
            # Save back to Excel
            output_file = f"cleaned_{filename}"
            df.to_excel(os.path.join(output_dir, output_file), index=False)
            print(f"  Successfully processed {len(df)} records in {filename}. Output saved to {output_file}")
            
        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
