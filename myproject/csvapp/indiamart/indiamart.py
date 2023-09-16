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
import base64
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.service import Service
import logging

logger = logging.getLogger(__name__)
# Setup the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token:
            creds = Credentials.from_authorized_user_file('token.json')

    # If there are no (valid) credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('csvapp/indiamart/'+'client_secret_355172851814-r55p4liplb4l4s309frpd97puut1eg4t.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def get_latest_email_subject(service):
    results = service.users().messages().list(userId='me', maxResults=1).execute()
    msg_id = results['messages'][0]['id']
    message = service.users().messages().get(userId='me', id=msg_id).execute()

    payload = message['payload']
    headers = payload['headers']

    for header in headers:
        name = header['name']
        if name == "Subject":
            return header['value']

    return None

def scrape(dir_name):
    service = Service(executable_path='csvapp/indiamart/chromedriver.exe')
    options = Options()

    options.add_argument('--user-data-dir=/Users/Administrator/AppData/Local/Google/Chrome/User Data/') 
    options.add_argument('--profile-directory=Profile 1')
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--start-maximized")

    options.add_argument('disable-infobars')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
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
    error = ""
    history = 1
    x = 0
    IsDriverClose = True
    for count,category in enumerate(categories):
        if IsDriverClose:
            driver = webdriver.Chrome(service=service,options=options )
            IsDriverClose = False

        for city in cities:

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
                driver = webdriver.Chrome(service=service,options=options )
                IsDriverClose = False

            try:
                wb_address = category + "?grid_view=1"
                wb_address = wb_address.replace("impcat",city)
                driver.get(wb_address)
                
                time.sleep(2)
                html_text = driver.page_source
                soup = BeautifulSoup(html_text,"lxml")
                


                if "No results found for" in html_text:
                    continue
                if "Oh no" in html_text:
                    continue


                soup_old = ""

                logger.info(f'Category Number:{count+1}/{len(categories)}----Dict_Length:{len(all_details)}')
               
                special_index = 0
                while True:
                    if special_index >=5:
                        break

                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    html_text = driver.page_source
                    soup = BeautifulSoup(html_text,"lxml")
                    if soup == soup_old:
                        break
                    else:
                        soup_old = soup
                    try:

                        btn = driver.find_element(By.CLASS_NAME,"fm2")
                        if btn:
                            driver.execute_script("arguments[0].click();",btn)
                        else:
                            special_index+=1
                            continue
                        html_text = driver.page_source
                        soup = BeautifulSoup(html_text,"lxml")
                        if "Email ID" in html_text:
                            email_input = driver.find_element(By.XPATH,"//*[@id='email']")
                            email_input.send_keys("waste5667@gmail.com")
                            time.sleep(1)
                            terms_btn = driver.find_element(By.XPATH,"//*[@id='myCheckbox']")
                            time.sleep(1)
                            terms_btn.click()
                            sign_in_btn = driver.find_element(By.XPATH,"//*[@id='submtbtn']")
                            sign_in_btn.click()
                            time.sleep(15)
                            serve = get_service()
                            subject = get_latest_email_subject(serve)
                            subject = subject.split("-")[1]
                            first_inp = driver.find_element(By.XPATH,"//*[@id='first']")
                            second_inp = driver.find_element(By.XPATH,"//*[@id='second']")
                            third_inp = driver.find_element(By.XPATH,"//*[@id='third']")
                            fourth_inp = driver.find_element(By.XPATH,"//*[@id='fourth']")
                            first_inp.send_keys(subject[0])
                            time.sleep(1)
                            second_inp.send_keys(subject[1])
                            time.sleep(1)
                            third_inp.send_keys(subject[2])
                            time.sleep(1)
                            fourth_inp.send_keys(subject[3])
                            time.sleep(1)

                    except:
                        error = "error in finding button"
                        x+=1
                        break

                    special_index+=1
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

    q_low = filtered_df["price"].quantile(0.10)
    q_hi  = filtered_df["price"].quantile(0.90)

    df_filtered = filtered_df[(filtered_df["price"] < q_hi) & (filtered_df["price"] > q_low)]
    
    # Calculate the average price per category
    summary_stats = df_filtered.groupby(["category","city"])['price'].agg(['mean', 'min', 'max', 'median'])
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
