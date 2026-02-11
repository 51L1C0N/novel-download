import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from urllib.parse import unquote, urljoin

# ================= 📝 用戶設定區 =================
# 小說檔名 (必填)
NOVEL_NAME = "AliceSW_Novel_31893" 

# 如果 JSON 裡讀不到目錄網址，才會用這個備用的
BACKUP_CATALOG_URL = "https://www.alicesw.com/other/chapters/id/31893.html" 

# 跳過前幾章 (預設 45)
SKIP_COUNT = 0 
# ===============================================

BASE_URL = "https://www.alicesw.com"

def load_config_from_json(filename="cookie.json"):
    """
    從 cookie.json 自動讀取 Cookie 字串，
    並嘗試尋找最後訪問的目錄頁面。
    """
    if not os.path.exists(filename):
        print(f"❌ 錯誤：找不到 {filename}，請確認檔案位置。")
        return None, None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. 組合 Cookie 字串
        cookie_parts = []
        target_url = None
        
        for item in data:
            name = item.get('name')
            value = item.get('value')
            if name and value:
                cookie_parts.append(f"{name}={value}")
                
            # 2. 嘗試自動抓取目錄 URL
            # 偵測 lf___forward__ 或類似欄位
            if name == "lf___forward__" and "chapters/id" in unquote(value):
                # 解碼網址 (把 %2F 變回 /)
                relative_path = unquote(value)
                target_url = urljoin(BASE_URL, relative_path)
                print(f"🎯 自動偵測到目錄網址: {target_url}")

        cookie_str = "; ".join(cookie_parts)
        return cookie_str, target_url

    except Exception as e:
        print(f"❌ 解析 JSON 失敗: {e}")
        return None, None

def get_soup(url, headers):
    for i in range(3):
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return BeautifulSoup(r.text, 'html.parser')
            elif r.status_code == 403:
                print("❌ 403 Forbidden: Cookie 可能已失效")
                return None
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return None

def main():
    print("📂 正在讀取 cookie.json ...")
    cookie_str, detected_url = load_config_from_json("cookie.json")
    
    if not cookie_str:
        return

    # 決定使用哪個網址 (自動偵測優先，否則用備用)
    catalog_url = detected_url if detected_url else BACKUP_CATALOG_URL
    print(f"🚀 目標目錄頁: {catalog_url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie_str,
        "Referer": BASE_URL
    }

    soup = get_soup(catalog_url, headers)
    if not soup:
        print("❌ 無法讀取目錄，請確認 Cookie 是否有效。")
        return

    # 抓取連結
    print("🔍 分析章節列表...")
    links = soup.select("a")
    valid_chapters = []
    
    for link in links:
        href = link.get('href')
        title = link.get_text().strip()
        # 過濾邏輯
        if href and "/book/" in href and len(title) > 1:
            full_url = urljoin(BASE_URL, href)
            if not any(c[1] == full_url for c in valid_chapters):
                valid_chapters.append((title, full_url))

    # 跳過前段
    if SKIP_COUNT > 0 and len(valid_chapters) > SKIP_COUNT:
        print(f"✂️ 跳過前 {SKIP_COUNT} 個連結 (可能是無效章節)...")
        valid_chapters = valid_chapters[SKIP_COUNT:]
    
    total = len(valid_chapters)
    print(f"📖 準備下載 {total} 章 (慢速安全模式)")

    filename = f"{NOVEL_NAME}.txt"
    with open(filename, "a", encoding="utf-8") as f:
        for index, (title, url) in enumerate(valid_chapters):
            print(f"[{index+1}/{total}] 下載: {title}")
            
            # 內層重試機制
            success = False
            for _ in range(3):
                try:
                    r = requests.get(url, headers=headers, timeout=15)
                    if r.status_code == 200:
                        r.encoding = 'utf-8'
                        page_soup = BeautifulSoup(r.text, 'html.parser')
                        # 抓取內文
                        content = page_soup.select_one("#content") or \
                                  page_soup.select_one(".read-content") or \
                                  page_soup.select_one(".novelcontent")
                        
                        if content:
                            # 清理
                            for tag in content(["script", "style", "div", "a", "iframe"]): 
                                tag.decompose()
                            text = content.get_text("\n\n", strip=True)
                            
                            f.write(f"\n\n{'='*20}\n{title}\n{'='*20}\n\n")
                            f.write(text)
                            f.flush()
                            success = True
                            break
                    time.sleep(2)
                except Exception:
                    time.sleep(2)
            
            if not success:
                print(f"   ⚠️ 下載失敗: {title}")
                f.write(f"\n\n[章節 {title} 下載失敗]\n\n")

            # 隨機延遲 5~8 秒
            delay = random.uniform(3, 5)
            time.sleep(delay)

    print("\n✅ 全部完成！")

if __name__ == "__main__":
    main()
