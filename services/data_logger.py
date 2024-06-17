import openpyxl
from openpyxl.utils import get_column_letter
import os
from datetime import datetime

def log_data(row_data):
    """Create a new Excel file or append to an existing one based on the date."""
    # Base directory for saving the file
    base_directory = '/home/pi/Documents/Logs'
    
    # Generate a filename based on the current month and year
    now = datetime.now()
    filename = f"Tools Issue {now.strftime('%B %Y')}.xlsx"
    full_path = os.path.join(base_directory, filename)
    
    headers = ['Date', 'Time', 'Operator Name', 'Tool Type', 'Tool Size', 'Quantity Issued', 'Quantity Received']

    # Check if the file exists
    if not os.path.exists(full_path):
        # Create a new workbook, add headers, and set column width
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(headers)
        for i, header in enumerate(headers, 1):
            sheet.column_dimensions[get_column_letter(i)].width = 20
    else:
        # Load the existing workbook
        workbook = openpyxl.load_workbook(full_path)
        sheet = workbook.active

    # Get current date and time
    current_date = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%I:%M:%S %p')  # 12-hour format with AM/PM

    # Prepend date and time to the row data
    full_row_data = [current_date, current_time] + row_data

    # Append the data
    sheet.append(full_row_data)
    workbook.save(full_path)
    print(f"Data saved to {full_path}")