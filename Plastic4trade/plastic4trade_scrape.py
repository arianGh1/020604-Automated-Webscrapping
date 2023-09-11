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

from multiprocessing import Process
from multiprocessing import Pool
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


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

with open("CategoryUrls","rb") as f:
    category_urls = pickle.load(f)
df = pd.DataFrame().from_dict(all_details).T