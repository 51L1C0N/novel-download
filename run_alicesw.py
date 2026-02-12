import main_engine
import plugin_alicesw as current_plugin

if __name__ == "__main__":
    # ================= 🔧 參數微調區 =================

    # 1. 小說設定
    main_engine.NOVEL_NAME = "AliceSW_小說下載"

    # 2. 關鍵設定：關閉智慧排版！
    # 因為 AliceSW 原本排版就不錯，插件裡已經用了 get_text("\n\n") 處理換行
    # 開啟這個會導致段落被錯誤合併
    main_engine.ENABLE_SMART_FORMAT = False

    # 3. 其他設定
    main_engine.USE_COOKIES = True           # 必須開啟
    main_engine.COOKIE_FILE = "cookie.json"  # 指定 Cookie 檔案
    main_engine.DELAY_RANGE = (3, 6)         # 速度控制

    # ===============================================

    print(f"🚀 啟動 AliceSW 任務 (排版修復: 關閉)")
    engine = main_engine.ScraperEngine(current_plugin)
    engine.run()
