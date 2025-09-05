import os
import configparser


class Writer:
    def __init__(self):
        # 到modules目錄
        modules_dir = os.path.dirname(__file__)  # __file__ 當前檔案    #dirname往上層找
        # 到根目錄
        root = os.path.dirname(modules_dir)
        # 找config.ini
        config_path = os.path.join(root, "config.ini")
        # 建立 ConfigParser
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding="utf-8-sig")
        self.html_file = self.config["file_name"]["html_file"]
        self.txt_file = self.config["file_name"]["txt_file"]

    def writer_html(self, datas):

        style = """
            <style>
                img,
                video {
                    margin: 10px;
                    max-width: 100%;
                    max-height: 300px;
                    height: auto;
                    width: auto;
                }
            </style>
            """

        # 處理資料
        body_contents = []
        collapse_id = 1
        for data in datas:
            number = data.get("number")
            url = data.get("url")

            keyword = data.get("keyword")

            news_cls = data.get("news_cls")
            if news_cls:
                news_cls = f'<h3>{data.get("news_cls")}</h3>'

            date = data.get("date")

            title = data.get("title")

            video = data.get("video")
            if video:
                video = f"""
                <video controls autoplay muted playsinline>
                    <source src="{data.get("video")}" type="video/mp4">
                </video>
                """

            imgs = []
            for img in data.get("imgs"):
                img_html = f'<img src="{img}">'
                imgs.append(img_html)

            contents = []
            for content in data.get("contents"):
                content_html = f"<p>{content}</p>"
                contents.append(content_html)

            body_content = f"""
            <div data-bs-toggle="collapse" data-bs-target="#collapse_{collapse_id}" style="cursor: pointer;">
                <h3>{title}</h3>
            </div>
            <div class="collapse" id="collapse_{collapse_id}" style='padding: 10px 40px; margin: 25px 20%; border: 5px solid black; border-radius: 8px;'>
                <div>
                    <h4>{number} 關鍵字：{keyword}</h4>
                    <a href="{url}">文章連結</a>
                    {news_cls}
                </div>
                <div>
                    <time>{date}</time>
                </div>
                <div>
                    <h1>{title}</h1>
                </div>
                <div>
                    {video}
                </div>
                <div style='display:flex; flex-wrap: wrap;'>
                    {'\n'.join(imgs)}
                </div>
                <div>
                    {'\n'.join(contents)}
                </div>
            </div>
            """

            body_contents.append(body_content)
            collapse_id += 1

        # 一次寫入
        with open(self.html_file, "w", encoding="utf-8-sig") as f:
            f.write(
                f"""
                    <html>
                    <head>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
                    {style}
                    </head>
                    <body>
                    <div class="d-flex justify-content-center align-items-center  min-vh-100 flex-column">
                        {'\n'.join(body_contents)}
                    </div>
                    </body>
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous"></script>
                    </html>
                    """
            )

    def writer_txt(self, datas):
        with open(self.txt_file, "w", encoding="utf-8-sig") as f:
            for data in datas:
                number = data.get("number")
                url = data.get("url")
                f.write(f"\n第 {number} 則  文章連結：{url}\n")

                news_cls = data.get("news_cls")
                title = data.get("title")
                f.write(f"{news_cls}\n{title}\n\n")

                video = data.get("video")
                f.write(f"影片連結：{video}\n")

                for img in data.get("imgs"):
                    f.write(f"照片連結：{img}\n")

                for content in data.get("contents"):
                    f.write(f"{content}\n")
