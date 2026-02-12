from urllib.parse import urljoin

# ================= 🔌 插件配置區 =================
# 1. 目標網址 (目錄頁)
CATALOG_URL = "https://czbooks.net/n/cpgjap8"

# 2. 網站特性標記
REVERSE_ORDER = False   # CZBooks 目錄通常是正序的 (第1章在最上面)，所以設 False
NEED_LOGIN = False      # 不需要登入

def parse_catalog(soup, base_url):
    """
    解析目錄頁，回傳 [(標題, 網址), ...] 列表
    """
    chapters = []

    # CZBooks 的章節列表在 <ul class="nav chapter-list"> 裡面
    chapter_list = soup.select("ul.nav.chapter-list li a")

    for link in chapter_list:
        title = link.get_text().strip()
        href = link.get('href')

        # 過濾空連結
        if href and title:
            # 補全網址 (雖然 CZBooks 通常是絕對路徑，但加上 urljoin 更保險)
            full_url = urljoin(base_url, href)
            # 簡單去重
            if not any(c[1] == full_url for c in chapters):
                chapters.append((title, full_url))

    return chapters

def parse_content(soup):
    """
    解析內文頁，回傳純文字
    """
    # CZBooks 的正文在 <div class="content"> 裡面
    content_div = soup.select_one("div.content")

    if content_div:
        # 移除廣告或雜訊 (CZBooks 有時會有 script 或 style)
        for trash in content_div(["script", "style", "div", "ins"]):
            trash.decompose()

        return content_div.get_text()

    return None
