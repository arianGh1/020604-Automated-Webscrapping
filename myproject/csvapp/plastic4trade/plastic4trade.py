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
import pickle

from multiprocessing import Process
from multiprocessing import Pool
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
def scrape(dir_name):
    options = Options()

    options.add_argument('--user-data-dir=/Users/Administrator/AppData/Local/Google/Chrome/User Data/') 
    options.add_argument('--profile-directory=Profile 1')
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

    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['acceptSslCerts'] = True
    capabilities['acceptInsecureCerts'] = True

    with open("csvapp/plastic4trade/CategoryUrls","rb") as f:
        category_urls = pickle.load(f)
    
    all_details = {}
    index = 0
    count = 0
    driver = webdriver.Chrome(executable_path='csvapp/plastic4trade/chromedriver.exe',options=options , desired_capabilities=capabilities)
    for category_url in category_urls:
        print(f'category: {category_url.split("/")[-2]} --{count}/{len(category_urls)}',end='\r')
        driver.get(category_url)
        time.sleep(3)
        try:
            sale_btn = driver.find_element(By.XPATH,"//*[@id='salepostcategory']/div/a/button")
            sale_btn.click()
        except:
            pass
        
        time.sleep(3)
        html_text = driver.page_source
        soup = BeautifulSoup(html_text,"lxml")
        products_part = soup.find("div",class_="news-detail-right-main")
        products = products_part.find_all("div",class_="col-lg-3 col-md-3 col-sm-12 col-xs-12")
        for product in products:
            details = {}

            details["name"] = product.find("h6").text
            details["link"] = product.find("a")["href"]
            details["price"] = product.find_all("div")[-1].text.strip()
            details["category"] = category_url.split("/")[-2]
            details["type"] = "sale"

            all_details[index] = details
            index += 1


        driver.get(category_url)
        time.sleep(3)
        try:
            buy_btn = driver.find_element(By.XPATH,"//*[@id='buypostcategory']/div/a/button")
            buy_btn.click()
        except:
            count+=1
            continue                             
        time.sleep(3)
        html_text = driver.page_source
        soup = BeautifulSoup(html_text,"lxml")
        products_part = soup.find("div",class_="news-detail-right-main")
        products = products_part.find_all("div",class_="col-lg-3 col-md-3 col-sm-12 col-xs-12")
    
        for product in products:
            details = {}
            
            details["name"] = product.find("h6").text
            details["link"] = product.find("a")["href"]
            details["price"] = product.find_all("div")[-1].text.strip()
            details["category"] = category_url.split("/")[-2]
            details["type"] = "buy"
            
            all_details[index] = details
            index += 1
        count+=1
        if count%5 == 0:
            driver.close()
            time.sleep(1)
            driver = webdriver.Chrome(executable_path='csvapp/plastic4trade/chromedriver.exe',options=options , desired_capabilities=capabilities)

    df = pd.DataFrame().from_dict(all_details).T
    del df["type"]
    df.to_csv(dir_name+"/plastic4trade.csv",index=False)
    
    df["price"] = df["price"].apply(lambda x: "@"+str(int(x.replace("$",""))*83) if "$" in x else x)
    df["price"] = df["price"].apply(lambda x: "@"+str(int(x.replace("£",""))*104) if "£" in x else x)
    df["price"] = df["price"].apply(lambda x: "@"+str(int(x.replace("€",""))*89) if "€" in x else x)
    df["price"] = df["price"].apply(lambda x: "@"+str(x.replace("₹","")) if "₹" in x else x)
    def process_price(value):
        if "@" not in value:
            return None
        try:
            return int(value.replace("@", ""))
        except ValueError:
            return None

    df["price"] = df["price"].apply(process_price)
    q_low = df["price"].quantile(0.10)
    q_hi  = df["price"].quantile(0.90)

    df_filtered = df[(df["price"] < q_hi) & (df["price"] > q_low)]
    summary_stats = df_filtered.groupby(["category"])['price'].agg(['mean', 'min', 'max', 'median'])
    summary_stats.to_csv(dir_name+"/summary.csv")
def generate():

    current_time = int(time.time())
    dir_name = 'csvapp/plastic4trade/plastic4trade_' + str(current_time)
    
    # Ensure the directory exists
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    scrape(dir_name)
   
    
    
    print(f"[{datetime.now()}] plastic4trade.csv has been generated!")

    zipf = zipfile.ZipFile(os.path.join(dir_name, 'plastic4trade.zip'), 'w', zipfile.ZIP_DEFLATED)
    
    for root, _, files in os.walk(dir_name):
        for file in files:
            if file.endswith('.csv'):
                zipf.write(os.path.join(root, file), file)
                
    zipf.close()

    return os.path.join(dir_name, 'plastic4trade.zip')

