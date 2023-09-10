import csv
from datetime import datetime
import zipfile
import os
import time
import pandas as pd
def generate():

    # Dummy data for demonstration purposes
    data = [
        ["Name", "Product", "Price"],
        ["Vendor A", "Widget A", "$134211"],
        ["Vendor B", "Widget B", "$12"]
    ]
    current_time = int(time.time())  # Current Unix timestamp


    dir_name = 'csvapp/plastic4trade/plastic4trade_' + str(current_time)
    
    # Ensure the directory exists
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    
   
    pd.DataFrame(data).to_csv(dir_name+'/plastic4trade.csv',index=False)
    
    print(f"[{datetime.now()}] plastic4trade.csv has been generated!")

    zipf = zipfile.ZipFile(os.path.join(dir_name, 'plastic4trade.zip'), 'w', zipfile.ZIP_DEFLATED)
    
    for root, _, files in os.walk(dir_name):
        for file in files:
            if file.endswith('.csv'):
                zipf.write(os.path.join(root, file), file)
                
    zipf.close()

    return os.path.join(dir_name, 'plastic4trade.zip')

