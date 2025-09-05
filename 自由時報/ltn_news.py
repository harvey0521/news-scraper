# 自由時報
import requests
from bs4 import BeautifulSoup
import configparser
import os
from modules.writer import Writer

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

# 抓文章的 selectors div
article_selectors = [  # 排除有 template 的 class
    "div.whitecon.article.boxTitle.boxText:not(.template)",
    "div.whitecon.article:not(.template)",
    "div.whitecon.boxTitle:not(.template)",
    "div.whitecon:not(.template)",
    "article.article",
    "section",
    "div.article_body",
]

news_data = []
for keyword in keywords:
    # 分頁 #抓類型、連結
    news_urls = []
    seen_hrefs = set()  # 排除一樣的連結
    page = 1
    num = 1
    while len(news_urls) < count:
        print(f"第{page}頁")
        search_url = f"https://search.ltn.com.tw/list?keyword={keyword}&page={page}"
        print(search_url)
        web = requests.get(search_url, verify=False)
        soup = BeautifulSoup(web.text, "html.parser")

        ul = soup.select_one("ul.list.boxTitle")

        if not ul:
            print("沒有更多新聞")
            break

        lis = ul.find_all("li")
        for li in lis:
            # 只補到所需的數量，不全抓
            if len(news_urls) >= count:
                break
            href = li.find("a")["href"]
            news_cls = li.find("i").getText().strip()  # 抓新聞類別
            print(f"第{num}則 新聞連結：{href}")

            # 如果已經抓過這個連結，就跳過
            if href in seen_hrefs:
                continue
            seen_hrefs.add(href)

            num += 1
            news_urls.append({"news_cls": news_cls, "href": href})

        page += 1

    # 進入連結抓內容
    num2 = 1
    for news_url in news_urls:
        web = requests.get(news_url["href"], verify=False)
        soup = BeautifulSoup(web.text, "html.parser")

        # 標題
        title = soup.find("h1")
        # title_html = str(title)
        title_text = title.get_text().strip()
        print(f"{num2}. {title_text}")

        # 找整個文章的 div
        for selector in article_selectors:
            article_div = soup.select_one(selector)
            if article_div:
                # print(article_div)
                break

        # 日期
        date = article_div.find('span', class_='time').get_text().strip()
        print(f'日期：{date}')

        # 圖片
        imgs_src = []
        try:
            imgs = article_div.find_all("img")
            for img in imgs:
                img_src = img.get("data-src") or img.get("src")
                print(f"照片連結：{img_src}")
                imgs_src.append(img_src)
        except AttributeError:
            print("此新聞沒有圖片")

        # 內文
        contents_text = []
        # 找整個文章 div 裡面內文的 div
        content_div = (
            article_div.select_one("div.text.boxTitle.boxText")
            or article_div.select_one("div.text.boxTitle")
            or article_div.select_one("div.text")
        )

        contents = content_div.find_all("p", recursive=False)  # 只找第一層的 p
        for content in contents:
            try:  # 跳過不要的內容
                skip_content = content.get("class")

                if "before_ir" in skip_content or "appE1121" in skip_content:
                    print("跳過")
                    continue
            except TypeError:
                print("沒有class屬性")

            content_text = content.get_text().strip()

            if not content_text:  # 排除 p 裡面是空的
                continue

            print(content_text)
            contents_text.append(content_text)

        news_data.append(
            {
                "number": num2,
                "keyword": keyword,
                "news_cls": news_url["news_cls"],
                "date": date,
                "url": news_url["href"],
                "title": title_text,
                "video": "",
                "imgs": imgs_src,
                "contents": contents_text,
            }
        )

        num2 += 1

# 寫入
writer = Writer()
writer.writer_html(news_data)
writer.writer_txt(news_data)
