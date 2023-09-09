import csv
from datetime import datetime
import zipfile
import os
def generate():
    # Dummy data for demonstration purposes
    data = [
        ["Name", "Product", "Price"],
        ["Vendor A", "Widget A", "$1011"],
        ["Vendor B", "Widget B", "$12"]
    ]

    dir_name = 'csvapp/indiamart'
    
    # Ensure the directory exists
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    csv_path = os.path.join(dir_name, 'indiamart.csv')

    # Generate a CSV file named 'indiamart.csv'
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    
    print(f"[{datetime.now()}] indiamart.csv has been generated!")

    zipf = zipfile.ZipFile(os.path.join(dir_name, 'indiamart.zip'), 'w', zipfile.ZIP_DEFLATED)
    
    for root, _, files in os.walk(dir_name):
        for file in files:
            if file.endswith('.csv'):
                zipf.write(os.path.join(root, file), file)
                
    zipf.close()

    return 'indiamart.zip'
