import gzip
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# 步驟 1：下載並解壓縮 Sitemap
sitemap_url = "http://tokyo-kitchen.icook.network/sitemaps/sitemap.xml.gz"
response = requests.get(sitemap_url)
if response.status_code == 200:
    with gzip.open(response.content, "rb") as f:
        xml_content = f.read()
    sitemap = ET.fromstring(xml_content)
else:
    print(f"無法下載 Sitemap，狀態碼: {response.status_code}")
    exit()

# 步驟 2：解析 Sitemap 並提取 URL
namespaces = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
urls = [url.text for url in sitemap.findall("ns:url/ns:loc", namespaces)]

# 步驟 3：逐一訪問 URL 並提取資料
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

for url in urls[:10]:  # 取前 10 個 URL 測試
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # 假設頁面標題為 <h1>
        title = soup.find("h1").text.strip() if soup.find("h1") else "無標題"
        print(f"URL: {url} | 標題: {title}")
    else:
        print(f"無法訪問 {url}，狀態碼: {response.status_code}")
