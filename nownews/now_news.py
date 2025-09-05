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

# 今日新聞有防爬蟲，判定送來的requests有沒有headers
# 要設假標頭
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
}


# 到ltn(自由時報)目錄
ltn_dir = os.path.dirname(__file__)  # __file__ 當前資料夾檔案    #dirname往上層找
# 到根目錄
root = os.path.dirname(ltn_dir)
# 找config.ini
config_path = os.path.join(root, "config.ini")
# 建立 ConfigParser
config = configparser.ConfigParser()
# 讀取 INI 設定檔  #config 出來的都會是字串
config.read(config_path, encoding="utf-8-sig")
# 關鍵字
keywords = config["settings"]["keywords"].split(" ")
print(keywords)
# 要抓的筆數
count = config["settings"].getint("count")  # 轉數字

news_data = []

for keyword in keywords:

    news_urls = []
    num = 1
    page = 1
    print(count)
    while len(news_urls) < count:
        search_url = f"https://www.nownews.com/search?q={keyword}&page={page}"
        print(search_url)

        driver.get(search_url)

        driver.find_element(By.ID, "btnQry").click()

        time.sleep(0.5)

        list_div = driver.find_element(By.CLASS_NAME, "item-list")
        urls = list_div.find_elements(By.TAG_NAME, "a")

        for url in urls:
            href = url.get_attribute("href")
            if len(news_urls) >= count:
                break
            if href in news_urls:
                continue
            print(f"{num} {href}")
            num += 1
            news_urls.append(href)

        page += 1

    # 進入連結抓內容
    num2 = 1
    for news_url in news_urls:
        web = requests.get(news_url, headers=headers, verify=False)
        soup = BeautifulSoup(web.text, "html.parser")

        # 類別
        news_cls_div = soup.find("div", class_="breadCrumbBlk")
        news_cls = news_cls_div.find_all("li")[2].get_text().strip()
        print(news_cls)

        # 標題
        title = soup.find("h1")
        title_text = title.get_text()

        print(title_text)

        # 日期
        date = soup.find("time", class_="time").get_text().strip()
        print(date)

        # 找整個文章的 div
        article_div = soup.find("div", id="news")

        # 照片
        imgs_src = []
        imgs = article_div.find_all("img")
        for img in imgs:
            imgs_src.append(img["src"])
        print(imgs_src)

        # 內文
        contents_text = []
        content_div = article_div.find("div", id="articleContent")
        content_text = content_div.get_text().strip()
        contents_text.append(content_text)
        print(content_text)
        # region
        # driver.get(news_url)
        # time.sleep(0.5)
        # content_div = driver.find_element(By.ID, "articleContent")
        # content_html = content_div.get_attribute('outerHTML')   #包含元素本身的 <div> 標籤與裡面的內容
        # content_soup = BeautifulSoup(content_html, "html.parser")
        # for unwanted in content_soup.select('#twitterPost, #instagramPost, img, figcaption'):
        #     unwanted.decompose()  # 從 DOM 中移除
        # clean_html = str(content_soup)
        # contents_text.append(clean_html)
        # print(clean_html)
        # endregion

        news_data.append(
            {
                "number": num2,
                "keyword": keyword,
                "news_cls": news_cls,
                "date": date,
                "url": url,
                "title": title_text,
                "video": "",
                "imgs": imgs_src,
                "contents": contents_text,
            }
        )
        num2 += 1

    writer = Writer()
    writer.writer_html(news_data)
    writer.writer_txt(news_data)
