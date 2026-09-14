# 東森新聞
# 需滾動、有連結會被鎖、截圖整頁面需使用 playwright 執行、截圖出 bytes 格式要轉 base64 格式，不需要額外的圖片檔案
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from playwright.sync_api import sync_playwright
import base64
import requests
from bs4 import BeautifulSoup
import configparser
import os
from modules.writer import Writer
import time

# 到ebc目錄
ebc_dir = os.path.dirname(__file__)  # __file__ 當前檔案    #dirname往上層找
# 到根目錄
root = os.path.dirname(ebc_dir)
# 找config.ini
config_path = os.path.join(root, "config.ini")
# 建立 ConfigParser
config = configparser.ConfigParser()
# 讀取 INI 設定檔  #config 出來的都會是字串
config.read(config_path, encoding="utf-8-sig")
# 關鍵字
keywords = config["keywords1"]["keywords1"].split(",")
# 要抓的筆數
count = config["settings"].getint("count")  # 轉數字 # 要抓的筆數
print(count)

service = Service("./msedgedriver.exe")
options = Options()
options.add_argument("--headless")  # 無界面模式
options.add_argument(
    "--disable-gpu"
)  # 禁用GPU加速，目前系統需要關閉才能無頭執行 (其他可能不需要)

driver = webdriver.Edge(service=service, options=options)


# 取得連結網頁html
def get_soup(url):
    try:
        web = requests.get(url, verify=False)
        return BeautifulSoup(web.text, "html.parser")
    except Exception as e:
        print(f"網頁取得失敗，錯誤訊息：{e}")


# 抓關鍵字首頁的標題連結
def get_url():
    a_tags = driver.find_elements(By.CSS_SELECTOR, ".list.m_group a")
    for a_tag in a_tags:
        # 數量到了就停止
        if len(news_urls) >= count:
            break

        href = a_tag.get_attribute("href")
        print(href)
        if href in news_urls:  # 如果已經抓過這個連結，就跳過
            continue

        soup = get_soup(href)  # 取得連結網頁html
        # 判斷連結是否鎖住
        is_lock = soup.find("center")

        if is_lock:
            print(f"此連結被封鎖跳過：{href}")
            continue

        news_urls.append(href)


news_data = []

for keyword in keywords:
    search_url = f"https://news.ebc.net.tw/search/keyword/{keyword}"

    driver.get(search_url)

    news_urls = []

    # 先抓取當下有的
    get_url()
    print(len(news_urls))

    list_div = driver.find_element(By.CSS_SELECTOR, ".list_box.row_box_group")

    # 初始整個內容高度 #看 list 高度方法
    last_height = driver.execute_script("return arguments[0].scrollHeight", list_div)
    print(f"初始{last_height}")

    while len(news_urls) < count:
        print(f"更新初始高度{last_height}")

        scroll_a_tags = driver.find_elements(By.CSS_SELECTOR, ".list.m_group a")

        driver.execute_script(
            "arguments[0].scrollIntoView();", scroll_a_tags[-1]
        )  # 把 scroll_a_tags 元素最後一項滾動到視窗中可見的位置(滑鼠滾輪滑到最後一個 scroll_a_tags 區塊)

        time.sleep(0.5)

        # 取當下有的
        get_url()

        # 最新 list 高度
        new_height = driver.execute_script("return arguments[0].scrollHeight", list_div)
        print(f"最新{new_height}")

        if new_height == last_height:
            print("沒有更多內容")
            break

        last_height = new_height  # 更新高度，繼續下一輪

    print(len(news_urls))

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge", headless=True
        )  # 或 "chrome" #headless=False 顯示視窗
        page = browser.new_page()  # 開新頁
        num = 1
        for news_url in news_urls:
            # browser = p.chromium.launch(channel="msedge", headless=False)
            # page = browser.new_page()
            page.goto(news_url)

            imgs = []
            # 取得全頁截圖的 bytes（不存檔）
            img_bytes = page.screenshot(full_page=True)
            img_b64 = base64.b64encode(img_bytes).decode("utf-8-sig")
            print(img_b64)

            # # 截取特定 container 的內容 bytes（不存檔）
            # img_bytes = page.locator(".container").nth(3).screenshot()
            # img_b64 = base64.b64encode(img_bytes).decode("utf-8-sig")
            # print(img_b64)

            imgs.append(img_b64)

            news_data.append(
                {"number": num, "keyword": keyword, "url": news_url, "imgs": imgs}
            )

            num += 1


writer = Writer()
writer.writer_html_img(news_data)
