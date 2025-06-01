import pandas as pd
import re
import os

folder_path = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(folder_path, 'input')
if not os.path.exists(input_dir):
    os.makedirs(input_dir)

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
        # Process each part separately and pick the first valid number
        parts = number_str.split('-')
        for part in parts:
            digits_only = re.sub(r'\D', '', part)
            if len(digits_only) >= 9:  # Found a valid-length number
                if digits_only.startswith('84'):
                    # Convert from +84 format to 0 format for prefix conversion
                    digits_only = '0' + digits_only[2:]
                elif not digits_only.startswith('0'):
                    digits_only = '0' + digits_only

                # Apply prefix conversion for Vietnamese numbers
                digits_only = convert_old_prefix(digits_only)
                
                # Convert back to international format and return just this number
                if digits_only.startswith('0'):
                    return '+84' + digits_only[1:]
                elif not digits_only.startswith('+84'):
                    return '+84' + digits_only
        
        # If we get here, no valid phone number was found
        return "WARNING: No valid phone number found"
    
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
    
    # Convert to local format for prefix conversion
    if digits.startswith('84'):
        digits = '0' + digits[2:]
    if not digits.startswith('0'): 
        digits = '0' + digits
        
    # Apply prefix conversion
    digits = convert_old_prefix(digits)
    
    # Format the phone number with international code
    if digits.startswith('0'):
        result = '+84' + digits[1:]
    elif not digits.startswith('+84'):
        result = '+84' + digits
    
    # Add back any parentheses content
    if parentheses_text:
        result += ' ' + parentheses_text
    
    return result

# Function to convert old number prefixes to new ones
def convert_old_prefix(phone_number):
    # Ensure phone_number is a string
    phone_number = str(phone_number)
    
    # Dictionary mapping old prefixes to new prefixes
    prefix_map = {
        '0162': '032', '0163': '033', '0164': '034', '0165': '035',
        '0166': '036', '0167': '037', '0168': '038', '0169': '039',
        '0120': '070', '0121': '079', '0122': '077', '0126': '076',
        '0128': '078', '0123': '083', '0124': '084', '0125': '085',
        '0127': '081', '0129': '082', '0188': '058', '0186': '056',
        '0199': '059'
    }
    
    # Check if phone number starts with any old prefix
    for old_prefix, new_prefix in prefix_map.items():
        if phone_number.startswith(old_prefix):
            return new_prefix + phone_number[len(old_prefix):]
    
    # Return original if no prefix match
    return phone_number


for filename in os.listdir(input_dir):
    if filename.endswith(".xlsx"):
        file_path = os.path.join(input_dir, filename)
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
                                             'Điện thoại', 'PHONE', 'Phone', 'Mobile', 'Tel',
                                             'Telephone', 'Contact', 'SỐ ĐIỆN THOẠI', 'ĐIỆN THOẠI']
                    
                    for col in possible_phone_columns:
                        if col in df.columns:
                            phone_column = col
                            found_header = True
                            header_row = test_row
                            break
                    
                    # If no named column found, look for columns with phone-like patterns
                    if not found_header:
                        best_match_col = None
                        max_phone_count = 0
                        
                        # Function to check if a string looks like a phone number
                        def looks_like_phone(s):
                            if pd.isna(s):
                                return False
                            digits = re.sub(r'\D', '', str(s))
                            return len(digits) >= 9 and len(digits) <= 15
                        
                        # Check each column for phone-like patterns
                        for col in df.columns:
                            # Count how many values in this column look like phone numbers
                            phone_like_count = df[col].apply(looks_like_phone).sum()
                            
                            # If more than 50% of non-empty cells look like phone numbers and it's better than previous best
                            if phone_like_count > 0:
                                non_empty_count = df[col].count()
                                if non_empty_count > 0 and phone_like_count/non_empty_count > 0.3 and phone_like_count > max_phone_count:
                                    max_phone_count = phone_like_count
                                    best_match_col = col
                        
                        if best_match_col:
                            phone_column = best_match_col
                            found_header = True
                            header_row = test_row
                            print(f"  Found likely phone column '{phone_column}' with {max_phone_count} phone-like values")
                    
                    if found_header:
                        print(f"  Found header at row {test_row+1} with column '{phone_column}'")
                        break
                        
                except Exception as e:
                    print(f"  Error reading header row {test_row}: {str(e)}")
                    continue  # Try next header row
            
            if not found_header:
                print(f"  Error: No valid header with phone column found in {filename}.")
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
            output_file = os.path.join(output_dir, output_file)
            df.to_excel(output_file, index=False)
            print(f"  Successfully processed {len(df)} records in {filename}. Output saved to {output_file}")
            
        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
