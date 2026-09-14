# 📰 News Scraper (自動化新聞輿情爬蟲系統)

![Status: Archived](https://img.shields.io/badge/Status-Archived-red)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Selenium](https://img.shields.io/badge/Selenium-Automated-green)
![Playwright](https://img.shields.io/badge/Playwright-Network_Intercept-orange)

> **⚠️ 狀態 (Status Notice):**
> 
> 本專案為過去任職公司期間所開發的業務工具。由於各大新聞網站的網頁結構 (DOM)、防爬蟲機制及 API 介面已隨著時間發生改變，本專案的程式碼**目前已無法直接運行**，僅作為技術展示與原始碼封存使用。

---

## 📖 專案簡介 (About The Project)

這是一個基於 Python 開發的自動化新聞擷取系統。在當時的業務場景中，團隊需要快速、大量地從多個主流新聞媒體收集特定關鍵字的最新報導，以利後續的輿情監測與資料分析。

本專案針對不同新聞平台的特性，混合使用了多種爬蟲技術（包含靜態請求、動態瀏覽器操作、網路請求攔截與全頁截圖），並將非結構化的網頁 HTML 轉換為乾淨的文字與視覺化的 HTML 報告，大幅節省了人工收集資料的時間。

### ✨ 核心功能與技術亮點 (Key Features)

* **多來源新聞解析**：針對 Yahoo 新聞、NOWnews (今日新聞)、自由時報 (LTN) 以及**東森新聞 (EBC)** 分別撰寫客製化的解析腳本，精準提取標題、日期、內文、圖片與影片。
* **動態網頁與無限捲動處理 (Selenium)**：針對需要動態加載的網站（如 Yahoo 新聞與東森新聞），使用 Selenium 控制 Edge 瀏覽器模擬真實使用者進行無限往下捲動與點擊換頁。
* **底層網路請求攔截 (Playwright)**：為了解決動態載入且隱藏在播放器內的影片網址，導入 Playwright 監聽並攔截底層的網路請求 (`request` 事件)，成功還原出真實的影音連結（如 Yahoo 新聞的 `m3u8` 播放源）。
* **全頁截圖突破限制**：針對連結易被封鎖或防護較嚴的網站（如東森新聞），使用 Playwright 進行無頭瀏覽器全頁截圖，並以 Base64 格式轉換，免去外部圖檔儲存的麻煩。
* **反爬蟲應對機制**：實作自訂 User-Agent 標頭、模擬等待延遲 (Time Sleep) 等機制，降低被目標網站封鎖的風險。
* **資料清洗與雜訊過濾 (BeautifulSoup)**：在萃取內文時，自動過濾掉不相關的網頁元素、廣告標籤（如 `read-more-vendor`、`appE1121` 等），確保文字乾淨度。
* **模組化報告產出 (Writer Module)**：將資料儲存邏輯獨立封裝為 `Writer` 類別，執行完畢後會自動產出三種格式：
  1. **TXT 純文字檔 (`news_output.txt`)**：方便後端系統或 NLP 模型進行文字分析。
  2. **HTML 視覺化報告 (`news_output.html`)**：引入 Bootstrap 5 前端框架，將爬取到的新聞以手風琴 (Collapse) 折疊面板的方式呈現，方便一般使用者閱讀。
  3. **Base64 截圖報告 (`news_img_output.html`)**：專供網頁截圖模式使用，將全頁截圖無縫嵌入 HTML。

## 🛠️ 技術棧 (Tech Stack)

* **核心語言**: `Python 3.x`
* **爬蟲與網頁自動化**: 
  * `Selenium` (WebDriver 控制, 處理 JS 動態渲染與無限捲動)
  * `Playwright` (非同步網路請求攔截與全頁截圖)
  * `Requests` (靜態 HTML 請求)
  * `BeautifulSoup4` (HTML DOM 節點解析與資料萃取)
* **設定與配置**: `configparser` (讀取外部 `.ini` 設定檔)
* **前端報告呈現**: `HTML`, `CSS`, `Bootstrap 5`, `Base64 Image Encoding`

## 📂 專案架構 (Architecture)

```text
news-scraper/
├── ebc_news.py          # 東森新聞爬蟲主程式 (含 Playwright 全頁截圖與 Base64 轉換)
├── yahoo_news.py        # Yahoo 新聞爬蟲主程式 (含 Playwright 請求攔截與 Selenium 捲動)
├── now_news.py          # NOWnews 爬蟲主程式 (Selenium 點擊與動態加載處理)
├── ltn_news.py          # 自由時報爬蟲主程式 (Requests + BS4 靜態解析)
├── modules/
│   └── writer.py        # 報表輸出模組 (負責產出 HTML 與 TXT)
├── config.ini           # 系統設定檔 (設定搜尋關鍵字 keywords、爬取筆數 count)
├── msedgedriver.exe     # Selenium Edge 瀏覽器驅動程式
├── news_output.html     # 爬蟲執行結果產出 (Bootstrap 視覺化報表)
├── news_output.txt      # 爬蟲執行結果產出 (純文字報表)
├── news_img_output.html # 爬蟲截圖結果產出 (Base64 圖片報表)
└── README.md            # 專案說明文件
