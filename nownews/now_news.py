# 今日新聞
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import requests
from bs4 import BeautifulSoup
import configparser
import os
from modules.writer import Writer
import time

service = Service("./msedgedriver.exe")
options = Options()
# options.add_argument("--headless")  # 無界面模式
# options.add_argument(
#     "--disable-gpu"
# )  # 禁用GPU加速，目前系統需要關閉才能無頭執行 (其他可能不需要)

driver = webdriver.Edge(service=service, options=options)


#到ltn(自由時報)目錄
ltn_dir = os.path.dirname(__file__) #__file__ 當前資料夾檔案    #dirname往上層找
#到根目錄
root = os.path.dirname(ltn_dir)
#找config.ini
config_path = os.path.join(root, 'config.ini')
# 建立 ConfigParser
config = configparser.ConfigParser()
# 讀取 INI 設定檔  #config 出來的都會是字串
config.read(config_path, encoding='utf-8-sig')
# 關鍵字
keywords = config['settings']['keywords'].split(' ')
print(keywords)
# 要抓的筆數
count = config["settings"].getint('count')  #轉數字 

news_data = []

for keyword in keywords:

    news_url = []
    num = 1
    page = 1
    print(count)
    while len(news_url) < count:
        search_url = f"https://www.nownews.com/search?q={keyword}&page={page}"
        print(search_url)

        driver.get(search_url)

        driver.find_element(By.ID, 'btnQry').click()

        time.sleep(1)

        list_div = driver.find_element(By.CLASS_NAME, 'item-list')
        urls = list_div.find_elements(By.TAG_NAME, 'a')

        for url in urls:
            href = url.get_attribute('href')
            if len(news_url) >= count:
                break
            if href in news_url:
                continue
            print(f'{num} {href}')
            num += 1
            news_url.append(href)
        
        page += 1
        