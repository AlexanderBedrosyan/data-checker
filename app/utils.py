from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from werkzeug.datastructures import FileStorage
import re


def extract_sheets_to_dicts(
    uploaded_file: FileStorage,
    sheet_names=("ICTemplateDataBS", "ReceivablePayable"),
):
    """
    Връща dict със sheet_name -> dict
    key = първа колона
    value = list с останалите колони (включително празни)
    """

    wb = load_workbook(uploaded_file, data_only=True)

    result = {}

    for sheet_name in sheet_names:
        if sheet_name not in wb.sheetnames:
            raise ValueError(f"Sheet '{sheet_name}' не съществува")

        ws = wb[sheet_name]
        sheet_dict = {}

        for row in ws.iter_rows(values_only=True):
            if not row:
                continue

            key = row[0]

            # ако първата колона е празна → пропускаме реда
            if key is None:
                continue

            if key not in sheet_dict:
                sheet_dict[key] = []

            if sheet_name == "ICTemplateDataBS":
                # за ICTemplateDataBS искаме само последната колона (ако има повече от 2)
                value = str(row[1]) + ' ' + str(row[-1])
                sheet_dict[key].append(value)
                continue

            values = [
                "" if cell is None else cell
                for cell in row[1:]
            ]

            sheet_dict[key] = values

        result[sheet_name] = sheet_dict
    return result


def column4_finder(first_row):
    for index, header in enumerate(first_row):
        if header.lower() == "column4" in str(header).lower():
            return index


def find_last_difference_column(header_row):
    """
    Find the last column that starts with 'Difference' in the header row.
    Returns the column index and the next difference number.
    """
    last_diff_index = -1
    max_diff_number = 0
    
    for index, header in enumerate(header_row):
        if header and isinstance(header, str) and header.startswith('Difference'):
            last_diff_index = index
            # Extract number from DifferenceN
            match = re.search(r'Difference(\d+)', header)
            if match:
                diff_number = int(match.group(1))
                if diff_number > max_diff_number:
                    max_diff_number = diff_number
    
    next_diff_number = max_diff_number + 1
    return last_diff_index, next_diff_number


def receivable_payable_preparation(data):
    pass

def ic_template_data_bs_preparation(data):
    """
    Prepare ICTemplateDataBS data.
    Returns a dict with company names as keys and their values.
    """
    final_report = {}

    for comp_name, details in data.items():
        if comp_name == "Company":  # Skip header row
            continue
            
        for element in details:
            element_parts = element.split()
            if len(element_parts) < 2:
                continue
                
            new_name = comp_name + " - " + element_parts[0]
            check_name = element_parts[0] + " - " + comp_name

            if check_name in final_report:
                continue

            try:
                final_report[new_name] = float(element_parts[-1])
            except (ValueError, IndexError):
                final_report[new_name] = 0.0

    return final_report


def process_excel_with_difference_logic(uploaded_file: FileStorage, output_path: str):
    """
    Main function to process the Excel file with the Difference column logic.
    
    Steps:
    1. Load the Excel file with formatting
    2. Find the last Difference column in ReceivablePayable sheet
    3. INSERT a new Difference column (not overwrite)
    4. Compare values from ICTemplateDataBS and populate the new column
    5. Apply color formatting (yellow or green)
    6. Add missing companies from ICTemplateDataBS as new rows
    7. Save the modified file
    """
    # Load workbook with formatting preserved
    wb = load_workbook(uploaded_file)
    
    # Define color fills
    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
    
    # Process ReceivablePayable sheet
    if "ReceivablePayable" not in wb.sheetnames:
        raise ValueError("Sheet 'ReceivablePayable' not found")
    
    rp_sheet = wb["ReceivablePayable"]
    
    # Get header row (first row)
    header_row = []
    company_col_index = None
    column4_col_index = None
    
    for col_idx, cell in enumerate(rp_sheet[1], start=1):
        header_value = cell.value
        header_row.append(header_value)
        
        if header_value == "Company":
            company_col_index = col_idx
        elif header_value == "Column4":
            column4_col_index = col_idx
    
    # Find last Difference column
    last_diff_col_index, next_diff_number = find_last_difference_column(header_row)
    
    if last_diff_col_index == -1:
        raise ValueError("No Difference column found in the header")
    
    # INSERT new column after the last Difference column
    # last_diff_col_index is 0-based, so +1 for column number, +1 for next position
    new_diff_col_index = last_diff_col_index + 2
    rp_sheet.insert_cols(new_diff_col_index)
    
    # Add new Difference column header
    new_diff_header = f"Difference{next_diff_number}"
    rp_sheet.cell(row=1, column=new_diff_col_index, value=new_diff_header)
    
    # Update column4_col_index if it was after the insertion point
    if column4_col_index and column4_col_index >= new_diff_col_index:
        column4_col_index += 1
    
    # Process ICTemplateDataBS sheet
    if "ICTemplateDataBS" not in wb.sheetnames:
        raise ValueError("Sheet 'ICTemplateDataBS' not found")
    
    # Extract ICTemplateDataBS data
    ic_data = {}
    ic_sheet = wb["ICTemplateDataBS"]
    
    for row in ic_sheet.iter_rows(min_row=2, values_only=True):  # Skip header
        if not row or row[0] is None:
            continue
        
        company_name = row[0]
        # Assuming format: Company | SomeCode | Value
        if len(row) >= 3:
            code = str(row[1]) if row[1] else ""
            value = row[-1]  # Last column value
            
            try:
                value_float = float(value) if value else 0.0
                # Only add if value is not zero
                if value_float != 0.0:
                    ic_data[company_name] = value_float
            except (ValueError, TypeError):
                pass
    
    # Track which companies from IC data were found in ReceivablePayable
    found_companies = set()
    
    # Process each row in ReceivablePayable (starting from row 2)
    for row_idx in range(2, rp_sheet.max_row + 1):
        company_cell = rp_sheet.cell(row=row_idx, column=company_col_index)
        company_name = company_cell.value
        
        if not company_name:
            continue
        
        # Get value from last Difference column (before insertion)
        last_diff_cell = rp_sheet.cell(row=row_idx, column=last_diff_col_index + 1)
        last_diff_value = last_diff_cell.value
        
        try:
            last_diff_value = float(last_diff_value) if last_diff_value else 0.0
        except (ValueError, TypeError):
            last_diff_value = 0.0
        
        # Look for matching company in ICTemplateDataBS
        matching_ic_value = None
        for ic_company, ic_value in ic_data.items():
            if company_name == ic_company or company_name in ic_company or ic_company in company_name:
                matching_ic_value = ic_value
                found_companies.add(ic_company)
                break
        
        # If no match found in IC data, skip this row
        if matching_ic_value is None:
            continue
        
        # Get Column4 value
        column4_cell = rp_sheet.cell(row=row_idx, column=column4_col_index) if column4_col_index else None
        column4_value = column4_cell.value if column4_cell else None
        
        # Apply logic
        new_cell = rp_sheet.cell(row=row_idx, column=new_diff_col_index)
        
        # Compare last_diff_value with matching_ic_value
        if abs(last_diff_value - matching_ic_value) > 0.01:  # Different values (with small tolerance)
            # Values are different -> add value and color yellow
            new_cell.value = matching_ic_value
            new_cell.fill = yellow_fill
        else:
            # Values match -> check Column4
            if not column4_value or column4_value == "":
                # Column4 is empty -> add value with yellow color
                new_cell.value = matching_ic_value
                new_cell.fill = yellow_fill
            else:
                # Column4 is not empty -> add value with green color
                new_cell.value = matching_ic_value
                new_cell.fill = green_fill
    
    # Add missing companies from ICTemplateDataBS as new rows
    missing_companies = set(ic_data.keys()) - found_companies
    
    if missing_companies:
        # Get the next empty row
        next_row = rp_sheet.max_row + 1
        
        for company_name in sorted(missing_companies):
            ic_value = ic_data[company_name]
            
            # Add company name in Company column
            rp_sheet.cell(row=next_row, column=company_col_index, value=company_name)
            
            # Add value in the new Difference column with yellow color (since it's new)
            new_cell = rp_sheet.cell(row=next_row, column=new_diff_col_index, value=ic_value)
            new_cell.fill = yellow_fill
            
            next_row += 1
    
    # Save the modified workbook
    wb.save(output_path)
    return output_path