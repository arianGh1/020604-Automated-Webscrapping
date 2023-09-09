import csv
from datetime import datetime

def generate():
    # Dummy data for demonstration purposes
    data = [
        ["Name", "Product", "Price"],
        ["Vendor A", "Widget A", "$10"],
        ["Vendor B", "Widget B", "$12"]
    ]

    # Generate a CSV file named 'indiamart.csv'
    with open('indiamart.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    
    print(f"[{datetime.now()}] indiamart.csv has been generated!")