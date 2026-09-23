"""
集中管理環境變數與常數設定
"""
import os
from pathlib import Path

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent

# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_USER_ID = os.environ.get("LINE_USER_ID", "")

# Groq API 設定
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# my-world API 設定
MY_WORLD_API_URL = os.environ.get("MY_WORLD_API_URL", "")
MY_WORLD_NEWS_API_KEY = os.environ.get("MY_WORLD_NEWS_API_KEY", "")

# Groq 模型設定
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_REASONING_EFFORT = "low"  # 摘要任務不需深度推理；推理 token 會計入 max_tokens
GROQ_MAX_TOKENS = 4096         # 含推理 token，2048 實測會截斷資安摘要

# RSS 來源設定檔路徑
RSS_SOURCES_PATH = PROJECT_ROOT / "rss_sources.json"

# 新聞過濾設定
NEWS_HOURS_LIMIT = 24          # 只取幾小時內的新聞
MAX_ARTICLES_PER_SOURCE = 5    # 每個來源最多取幾篇
MAX_ARTICLES_FOR_SUMMARY = 20  # 傳給 Groq 最多幾篇

# LINE 訊息設定
LINE_MESSAGE_MAX_LENGTH = 5000  # LINE 單則訊息最大字元數

# 驗證必要環境變數
def validate_config() -> None:
    """檢查必要的環境變數是否已設定，若缺少則拋出例外"""
    missing = []
    if not LINE_CHANNEL_ACCESS_TOKEN:
        missing.append("LINE_CHANNEL_ACCESS_TOKEN")
    if not LINE_USER_ID:
        missing.append("LINE_USER_ID")
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")

    if missing:
        raise EnvironmentError(
            f"缺少必要的環境變數：{', '.join(missing)}\n"
            "請參考 .env.example 設定環境變數。"
        )
