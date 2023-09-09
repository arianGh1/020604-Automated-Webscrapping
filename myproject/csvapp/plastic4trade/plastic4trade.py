import csv
from datetime import datetime
import zipfile
import os
def generate():
    # Dummy data for demonstration purposes
    data = [
        ["Name", "Material", "Quantity"],
        ["Supplier X", "Polyethylene", "1000 kg"],
        ["Supplier Y", "Polypropylene", "2000 kg"]
    ]


    dir_name = 'csvapp/plastic4trade'
    
    # Ensure the directory exists
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    csv_path = os.path.join(dir_name, 'plastic4trade.csv')

    # Generate a CSV file named 'plastic4trade.csv'
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    
    print(f"[{datetime.now()}] plastic4trade.csv has been generated!")

    zipf = zipfile.ZipFile(os.path.join(dir_name, 'plastic4trade.zip'), 'w', zipfile.ZIP_DEFLATED)
    
    for root, _, files in os.walk(dir_name):
        for file in files:
            if file.endswith('.csv'):
                zipf.write(os.path.join(root, file), file)
                
    zipf.close()

    return 'plastic4trade.zip'