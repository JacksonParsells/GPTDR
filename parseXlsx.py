import openpyxl
import json

# Open the xlsx file and select the active sheet
workbook = openpyxl.load_workbook('sub_saharan_health_facilities.xlsx')
sheet = workbook.active

# Create an empty list to store the data
data = []

# Define a list of the column numbers you want to include
columns_to_include = [1, 3, 6, 7]

# Iterate through each row in the sheet (excluding the first row)
for row in sheet.iter_rows(min_row=2, values_only=True):
    # Create a dictionary to store the values from the selected columns
    row_data = {
        'Country': row[0] ,
        'Hospital Name': row[2] ,
        'Latitude': row[5] ,
        'Longitude': row[6] 
    }
    # Add the row data to the list of data
    data.append(row_data)

# Convert the data list to JSON format and print it
# json_data = json.dumps(data, indent=4)
# print(json_data)

with open('hospitals.json', 'w') as f:
    json.dump(data, f, indent=4)
