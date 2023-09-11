import csv
from datetime import datetime
import zipfile
import os
import time
import pandas as pd
import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import pickle
import numpy as np
import pandas as pd
import pickle
from scipy import stats

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

def scrape(dir_name):
    options = Options()

    options.add_argument('--user-data-dir=/Users/Arian_Gh/AppData/Local/Google/Chrome/User Data/') 
    options.add_argument('--profile-directory=Profile 4')
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--start-maximized")

    options.add_argument('disable-infobars')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--remote-debugging-port=9222")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}')

    prefs = {
        "profile.default_content_setting_values.images": 2
    }
    options.add_experimental_option("prefs", prefs)

    # Add a preference to disable image loading

    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['acceptSslCerts'] = True
    capabilities['acceptInsecureCerts'] = True


    file_path = 'csvapp/indiamart/'+'urls.txt'

    categories = []

    with open(file_path, 'r') as file:
        for line in file:     
            category = line.strip()
            categories.append(category)
    file_path = 'csvapp/indiamart/'+'cities.txt'

    cities = []

    with open(file_path, 'r') as file:
        for line in file:     
            cityy = line.strip().lower()
            cities.append(cityy)



    all_details = {}
    index = 0
    urls = []
    names = []
    error = ""
    history = 1
    x = 0
    IsDriverClose = True
    for count,category in enumerate(categories[:2]):
        if IsDriverClose:
            driver = webdriver.Chrome(executable_path='csvapp/indiamart/chromedriver.exe',options=options )
            IsDriverClose = False

        for city in cities[:5]:

            if history%24==0 :

                if not IsDriverClose:
                    driver.close()
                    IsDriverClose = True
                    
                else:
                    x+=1
                history+=1

            else:
                history += 1

            if IsDriverClose:
                time.sleep(3)
                driver = webdriver.Chrome(executable_path='csvapp/indiamart/chromedriver.exe',options=options )

            try:
                wb_address = category + "?grid_view=1"
                wb_address = wb_address.replace("impcat",city)
                driver.get(wb_address)
                
                time.sleep(4)
                html_text = driver.page_source
                soup = BeautifulSoup(html_text,"lxml")
                
                # If captcha appears
                while "check the box below to proceed" in html_text:
                    print("Stucked in the Captcha , please check the box to continue","r")
                    html_text = driver.page_source
                    soup = BeautifulSoup(html_text,"lxml")
                    continue

                if "No results found for" in html_text:
                    continue
                if "Oh no" in html_text:
                    continue


                soup_old = ""
                print(f'Category Number:{count+1}/{len(categories)}----Dict_Length:{len(all_details)}',end='\r')
                while True:


                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    html_text = driver.page_source
                    soup = BeautifulSoup(html_text,"lxml")
                    if soup == soup_old:
                        break
                    else:
                        soup_old = soup
                    try:

                        btn = driver.find_element(By.CLASS_NAME,"fm2")
                        driver.execute_script("arguments[0].click();",btn)

                    except:
                        error = "error in finding button"
                        x+=1
                        break
                html_text = driver.page_source
                soup = BeautifulSoup(html_text,"lxml")
                products = soup.find("div",class_="q_hm1 cnhdr fxmn")
                products = products.find("div",class_='lay-left')
                products = products.find("ul",class_="mListGrp w100 sid_df fww wlm mFrgn")
                sections = products.find_all("li")
                filtered_sections = []

                for section in sections:
                    if section.has_attr('id'):
                        filtered_sections.append(section)

                for section in filtered_sections:
                    details={}
                    try:
                        name = section.find("h3").text
                        price = section.find("p").text
                        try:
                            url = section.find('li',class_="mListPrc").find("a")["href"]
                        except:
                            try:
                                url = section.find("a")["href"]
                            except:
                                url = None
                            
                    except:
                        
                        continue

                    details["name"]= name
                    details["price"] = price
                    details["url"] = url
                    details["category"] = category.split("/")[-1].split(".html")[0]
                    details["city"] = city

                    all_details[index] = details
                    index+=1
            except:
                error = "error in big try"
                x+=1
                continue
        if not IsDriverClose:
            driver.close()
            IsDriverClose = True
        else:
            x+=1

            
        time.sleep(2)


    df = pd.DataFrame().from_dict(all_details).T
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    df.to_csv(dir_name+"/indiamart.csv",index=False)


    df["price"] = df["price"].apply(lambda x: str(x).strip(" "))
    df["price"] = df["price"].apply(lambda x: str(x).lower())

    df["price"] = df["price"].apply(lambda x: str(x).replace("Kilogram","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("Kg","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("KG","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("Kilogram(s)","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("KILOGRAMS","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("kgs","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("kilogram","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("kg(s)","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("per kg","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("kgs","kg"))

    df["price"] = df["price"].apply(lambda x: str(x).replace("kg onwards","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("Kilogram Onwards","kg"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("TONNE","tonne"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("Tonne","tonne"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("metric ton(s)","tonne"))
    df["price"] = df["price"].apply(lambda x: str(x).replace("ton","tonne") if str(x).split("/")[-1]==" ton" else x)
    df["price"] = df["price"].apply(lambda x: str(x).replace("metric ton","tonne"))

    df["price"] = df["price"].apply(lambda x: str(x).replace("Ton","tonne"))

    df["metric"] = df["price"].apply(lambda x: str(x).split("/")[-1].strip())


    names_to_filter = ["kg", "tonne", "metric"]
    filtered_df = df[df['metric'].isin(names_to_filter)]
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.to_csv(dir_name+"/filtered_indiamart.csv",index=False)

    filtered_df["price"] = filtered_df["price"].apply(lambda x: float(x.split("/")[0].replace("₹","").replace(",","").split(" ")[0])/1000 if x.split("/")[1]==" tonne" else float(x.split("/")[0].replace("₹","").replace(",","").split(" ")[0]))
    del filtered_df["metric"]
    filtered_df['z_score'] = stats.zscore(filtered_df['price'])

    # Remove outliers: keep only the ones that are within +3 to -3 standard deviations in the column 'price'
    filtered_df = filtered_df[filtered_df['z_score'].abs() <= 3]

    # Drop the Z-score column as we no longer need it
    filtered_df.drop(columns=['z_score'], inplace=True)

    filtered_df.to_csv("filtered_indiamart.csv",index=False)
    # Calculate the average price per category
    summary_stats = filtered_df.groupby(["category","city"])['price'].agg(['mean', 'min', 'max', 'median'])
    summary_stats.to_csv(dir_name+"/summary.csv")

def generate():
    current_time = int(time.time())
    dir_name = 'csvapp/indiamart/indiamart_' + str(current_time)
    
    # Current Unix timestamp
    # Ensure the directory exists
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    scrape(dir_name)
    print(f"[{datetime.now()}] indiamart.csv has been generated!")

    zipf = zipfile.ZipFile(os.path.join(dir_name, 'indiamart.zip'), 'w', zipfile.ZIP_DEFLATED)
    
    for root, _, files in os.walk(dir_name):
        for file in files:
            if file.endswith('.csv'):
                zipf.write(os.path.join(root, file), file)
                
    zipf.close()

    return os.path.join(dir_name, 'indiamart.zip')
