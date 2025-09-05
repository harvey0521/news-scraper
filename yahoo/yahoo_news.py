# yahoo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import configparser
import os
from modules.writer import Writer
import time

#到yahoo目錄
yahoo_dir = os.path.dirname(__file__) #__file__ 當前檔案    #dirname往上層找
#到根目錄
root = os.path.dirname(yahoo_dir)
#找config.ini
config_path = os.path.join(root, 'config.ini')
# 建立 ConfigParser
config = configparser.ConfigParser()
# 讀取 INI 設定檔  #config 出來的都會是字串
config.read(config_path, encoding='utf-8-sig')
# 關鍵字
keywords = config['settings']['keywords'].split(' ')
# 要抓的筆數
count = config["settings"].getint('count')  #轉數字 # 要抓的筆數

# 抓關鍵字首頁的標題連結
def get_url():
    h3s = driver.find_elements(By.TAG_NAME, "h3")
    for h3 in h3s[:count]:  # 取前count筆數
        a = h3.find_element(By.TAG_NAME, "a")
        href = a.get_attribute("href")
        # print(f"{h3.text}\n{href}")
        # print(href)
        if href in news_urls:  # 去除重複的
            continue

        news_urls.append(href)


# 抓影片網址 使用 playwright 模組找網路請求
def get_video_url(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge", headless=True
        )  # 或 "chrome" #headless=False 顯示視窗
        page = browser.new_page()

        video_url = ""

        def handle_requests(request):
            nonlocal video_url  # nonlocal 只能用在內部函式修改外部函式的變數 #如果外部沒有函式，就要用 global
            if "https://edge-auth.api.brightcove.com" in request.url:
                try:
                    response = request.response()
                    data = response.json()
                    video_url = data["sources"][2]["src"]
                    print(f"抓出來的影片連結：{video_url}")
                except:
                    print("沒有影片")

        page.on(
            "requestfinished", handle_requests
        )  # 網路請求「完全完成」時才觸發 #請求已完成，回應內容已下載完
        page.goto(url)
        page.wait_for_timeout(1000)  # 等待1秒確保網頁發送請求
        browser.close()
        return video_url


service = Service("./msedgedriver.exe")
options = Options()
options.add_argument("--headless")  # 無界面模式
options.add_argument(
    "--disable-gpu"
)  # 禁用GPU加速，目前系統需要關閉才能無頭執行 (其他可能不需要)


driver = webdriver.Edge(service=service, options=options)

news_data = []

for keyword in keywords:
    search_url = f"https://tw.news.yahoo.com/search?p={keyword}"

    driver.get(search_url)

    time.sleep(2)

    news_urls = []

    # 先抓取當下有的
    get_url()

    # 找到真正滾動得元素
    scroll_div = driver.find_element(By.ID, "stream-container-scroll-template")

    # 整個內容高度
    print(driver.execute_script("return arguments[0].scrollHeight", scroll_div))

    # 初始整個內容高度 #看 ul 高度方法
    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_div)
    print(f"ul 初始整個內容高度{last_height}")

    # region 看 li 數量方法
    # li = driver.find_elements(By.CLASS_NAME, "StreamMegaItem")
    # last_height = len(li)
    # print(f"初始 li 數量為 {last_height}")
    # endregion

    while len(news_urls) < count:  # 目前抓到筆數

        # 看 ul 高度方法
        li = driver.find_elements(By.CLASS_NAME, "StreamMegaItem")

        # 往下滾動
        driver.execute_script(
            "arguments[0].scrollIntoView();", li[-1]
        )  # 把 li 元素最後一項滾動到視窗中可見的位置(滑鼠滾輪滑到最後一個 li 區塊)

        time.sleep(2)

        # 抓取當下有的
        get_url()

        # 新整個內容高度 #看 ul 高度方法
        new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_div)
        print(f"ul 最新整個內容高度{new_height}")

        # region 看 li 數量方法
        # li = driver.find_elements(By.CLASS_NAME, "StreamMegaItem")
        # new_height = len(li)
        # print(f"最新 li 數量 {new_height}")
        # endregion

        if new_height == last_height:
            print("沒有新內容了，停止滾動")
            break  # 沒有新內容了，停止滾動
        print(f"目前網址數量：{len(news_urls)}")

        last_height = new_height  # 更新高度，繼續下一輪


    print(f"網址數量共：{len(news_urls)}")

    # driver.quit()  # 關閉自動操作  #退出後後面就不能使用 driver
    # driver.close()  #暫時關閉


    # 進入連結抓內容
    num = 1
    for news_url in news_urls:
        web = requests.get(news_url, verify=False)
        soup = BeautifulSoup(web.text, "html.parser")

        print(f"第{num}筆")

        # 抓標題
        try:
            header = soup.find("header", class_="mb-module-gap")
            title = header.find("h1")
            
            #抓影片
            videoUrl = get_video_url(news_url)
            print(title)
        except AttributeError:  # 如果沒有找到 title 代表他還有一頁需要再進入 (新聞專輯)
            print("還有一頁需再進入")
            driver.get(news_url)
            # time.sleep(2)
            a_div = driver.find_element(By.ID, "TopicHero")
            print("找到 a_div")
            new_url = a_div.find_element(By.TAG_NAME, "a").get_attribute("href")
            print(f"新的連結{new_url}")
            web = requests.get(new_url, verify=False)
            soup = BeautifulSoup(web.text, "html.parser")
            header = soup.find("header", class_="mb-module-gap")
            title = header.find("h1")
            #抓影片
            videoUrl = get_video_url(new_url)
            print(title)

        title_text = title.get_text().strip()
        print(title_text)

        atoms = soup.find_all("div", class_="atoms")

        #日期
        date = soup.find('time').get_text().strip()
        print(f'日期：{date}')

        print(f"影片連結：{videoUrl}")


        # 抓圖片
        imgs_src = []
        for atom in atoms:
            imgsFigures = atom.find_all("figure")
            if imgsFigures:
                for imgsFigure in imgsFigures:
                    imgs = imgsFigure.find_all("img")
                    for img in imgs:
                        img_src = img["src"]
                        imgs_src.append(img_src)

        print(len(atoms))

        # 抓內文
        contents_text = []
        if len(atoms) > 1:  # 如果有兩個就取第二個

            contents = atoms[1].find_all("p", recursive=False)  # 只找第一層的 p

        else:

            contents = atoms[0].find_all("p", recursive=False)  # 只找第一層的 p

        for content in contents:

            skip_content = content["class"]

            if "read-more-vendor" in skip_content or "read-more-editor" in skip_content:
                print("跳過")
                continue

            contentHtml = str(content)
            content_text = content.get_text().strip()
            contents_text.append(content_text)

            print(contentHtml)

        news_data.append(
            {
                "number": num,
                'keyword':keyword,
                "news_cls": "",
                "date": date,
                "url": news_url,
                "title": title_text,
                "video": videoUrl,
                "imgs": imgs_src,
                "contents": contents_text,
            }
        )

        num += 1

writer = Writer()
writer.writer_html(news_data)
writer.writer_txt(news_data)