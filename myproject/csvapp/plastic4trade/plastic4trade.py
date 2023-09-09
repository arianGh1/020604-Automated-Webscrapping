import csv
from datetime import datetime

def generate():
    # Dummy data for demonstration purposes
    data = [
        ["Name", "Material", "Quantity"],
        ["Supplier X", "Polyethylene", "1000 kg"],
        ["Supplier Y", "Polypropylene", "2000 kg"]
    ]

    # Generate a CSV file named 'plastic4trade.csv'
    with open('plastic4trade.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    
    print(f"[{datetime.now()}] plastic4trade.csv has been generated!")