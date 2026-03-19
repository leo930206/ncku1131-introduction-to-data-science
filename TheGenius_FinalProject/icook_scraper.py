import json
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------------------------------------------------
# 函式：fetch_page_with_selenium
# 功能：使用 Selenium 以無頭模式獲取動態加載的網頁內容。
#       同時透過 webdriver_manager 幫忙自動管理 ChromeDriver。
# 回傳：成功時回傳網頁 HTML (str)，失敗時回傳 None。
# ---------------------------------------------------------------------
def fetch_page_with_selenium(url):
    """
    使用 Selenium 獲取動態加載的網頁內容，並使用 webdriver_manager 自動管理 ChromeDriver。
    """
    # 設定 Chrome 選項
    chrome_options = Options()
    chrome_options.add_argument('--headless')            # 無頭模式
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')  # 防止資源不足
    chrome_options.add_argument('--window-size=1920,1080')  # 設定視窗大小
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/115.0.0.0 Safari/537.36'
    )  # 設定 User-Agent

    # 隱藏 Selenium 在瀏覽器中的自動化特徵
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 初始化 WebDriver
    try:
        # 透過 webdriver_manager 自動安裝並設定 ChromeDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"初始化 WebDriver 時出錯: {e}")
        return None

    # 隱藏 webdriver 屬性 (進一步降低被網站偵測的可能性)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    try:
        # 進入指定的 URL
        driver.get(url)

        # 顯式等待：等待頁面內標籤 <h1> 出現，最多等 15 秒
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))

        # 模擬滾動到底部，以確保所有動態內容皆被加載
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # 滾動後等待 5 秒，讓新內容載入完成

        # 取得整個頁面的 HTML 原始碼
        page_content = driver.page_source

        # ---------------- 調試用 ----------------
        # 將抓取到的 HTML 存檔到本地，以便手動檢查是否抓到預期內容
        with open('fetched_page.html', 'w', encoding='utf-8') as f:
            f.write(page_content)
        print("已將抓取到的 HTML 保存到 'fetched_page.html'。請檢查此文件以確認內容。")

        return page_content

    except Exception as e:
        print(f"Selenium 獲取網頁內容時出錯: {e}")
        return None
    finally:
        # 無論成功或失敗，都要關閉瀏覽器
        driver.quit()

# ---------------------------------------------------------------------
# 函式：parse_recipe
# 功能：使用 BeautifulSoup 解析 HTML，提取並回傳食譜的關鍵資訊：
#       包含食物名稱、標籤、食材、步驟、份量與時間。
# 回傳：返回一個 dictionary，包含提取到的各種屬性。
# ---------------------------------------------------------------------
def parse_recipe(html_content):
    """
    使用 BeautifulSoup 解析 HTML 並提取食譜數據。
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. 提取食物名稱
    food_name = None
    h1_tag = soup.find('h1')
    if h1_tag:
        food_name = h1_tag.get_text(strip=True)
    else:
        print("無法找到食物名稱。")

    # 2. 提取標籤（Hashtags），以 # 開頭的字串
    hashtag_list = []
    hashtags = soup.find_all('a', text=lambda x: x and x.startswith('#'))
    if hashtags:
        hashtag_list = [tag.get_text(strip=True) for tag in hashtags]
    else:
        print("無法找到標籤。")

    # 3. 提取食材
    ingredients = []
    # 先找所有 class='group' 的容器
    ingredient_groups = soup.find_all('div', class_='group')

    for group in ingredient_groups:
        group_name = group.find('div', class_='group-name')
        # 尋找 class='ingredient' 的 <li>
        ingredient_items = group.find_all('li', class_='ingredient')
        for item in ingredient_items:
            name_tag = item.find('div', class_='ingredient-name')
            unit_tag = item.find('div', class_='ingredient-unit')
            if name_tag and unit_tag:
                ingredient_name = name_tag.get_text(strip=True)
                ingredient_unit = unit_tag.get_text(strip=True)
                ingredients.append(f"{ingredient_name} {ingredient_unit}")

    # 4. 提取步驟 (class='recipe-step-description-content')
    steps = []
    step_items = soup.find_all('p', class_='recipe-step-description-content')
    for step_item in step_items:
        step_text = step_item.get_text(strip=True)
        if step_text:
            # 先根據換行符切分
            split_steps = [s.strip() for s in step_text.split('\n') if s.strip()]
            # 再移除一些特殊符號 (●, 🔹)
            cleaned_steps = [re.sub(r'[●🔹]', '', step).strip() for step in split_steps]
            steps.extend(cleaned_steps)

    if not steps:
        print("無法找到步驟列表。")

    # 5. 提取份量
    servings = "未提供"
    servings_selectors = [
        {'name': 'span', 'class_': 'servings'},
        {'name': 'div', 'class_': 'servings'},
        {'name': 'p', 'class_': 'servings'},
        {'name': 'span', 'class_': 'recipe-servings'}
    ]
    for selector in servings_selectors:
        servings_tag = soup.find(selector['name'], class_=selector['class_'])
        if servings_tag:
            servings = servings_tag.get_text(strip=True)
            break
    if servings == "未提供":
        print("無法找到份量信息。")

    # 6. 提取時間
    time_text = "未提供"
    time_selectors = [
        {'name': 'span', 'class_': 'time'},
        {'name': 'div', 'class_': 'time'},
        {'name': 'p', 'class_': 'time'},
        {'name': 'span', 'class_': 'recipe-time'}
    ]
    for selector in time_selectors:
        time_tag = soup.find(selector['name'], class_=selector['class_'])
        if time_tag:
            time_text = time_tag.get_text(strip=True)
            break

    if time_text == "未提供":
        # 使用正則表達式在整個頁面中搜索 "XX 分鐘"
        match = re.search(r'(\d+)\s*分鐘', soup.get_text())
        if match:
            time_text = f"{match.group(1)} 分鐘"
            print("已使用正則表達式抓取時間。")
        else:
            print("無法找到時間信息。")

    # 整合數據到一個 dictionary
    recipe_data = {
        '食物': food_name if food_name else "未提供",
        '標籤': hashtag_list,
        '食材': ingredients,
        '步驟': steps,
        '份量': servings,
        '時間': time_text
    }

    return recipe_data

# ---------------------------------------------------------------------
# 函式：save_recipes_to_json
# 功能：將收集到的所有食譜資料存成 JSON 檔，使用 UTF-8 編碼。
# ---------------------------------------------------------------------
def save_recipes_to_json(recipes, filename='recipes.json'):
    """
    將食譜數據保存為 JSON 文件。
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=4)
    print(f"所有食譜數據已保存到 {filename}")

# ---------------------------------------------------------------------
# 函式：main
# 功能：主要程式流程，定義要抓取的食譜 URL 清單，逐一抓取並解析，
#       最後將結果存成 JSON 檔。
# ---------------------------------------------------------------------
def main():
    # 目標網頁的 URL (在此可添加更多食譜 URL)
    recipe_urls = [
        "https://icook.tw/recipes/473291",
        "https://icook.tw/recipes/474458",
    ]
    # 用於存放所有解析好的食譜資料
    recipes = []

    # 逐一抓取每個 URL
    for url in recipe_urls:
        print(f"抓取食譜: {url}")
        html_content = fetch_page_with_selenium(url)
        # 若成功取得 HTML，則解析食譜並加入 recipes 清單中
        if html_content:
            recipe = parse_recipe(html_content)
            recipes.append(recipe)

    # 將所有食譜存成 JSON 檔
    save_recipes_to_json(recipes)

# ---------------------------------------------------------------------
# 程式入口
# 若此檔案是主程式被執行，則呼叫 main() 進行爬蟲流程。
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()