"""
每日 AI 新聞彙整 LINE Bot 主程式

執行流程：
1. 驗證環境變數
2. 抓取 RSS Feed（24小時內新聞）
3. 使用 Claude API 整理摘要
4. 透過 LINE Push Message 發送
"""
import logging
import sys
from datetime import datetime, timezone, timedelta

# 確保 src/ 在 import 路徑中（本機執行時）
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import validate_config
from rss_fetcher import fetch_articles
from news_processor import process_news
from line_sender import send_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("=== 每日 AI 新聞彙整開始 ===")

    # 1. 驗證環境變數
    logger.info("步驟 1/4：驗證環境變數")
    validate_config()

    # 取得台灣時間（UTC+8）的日期作為標題日期
    tw_time = datetime.now(tz=timezone(timedelta(hours=8)))
    date_str = tw_time.strftime("%Y-%m-%d")
    logger.info("今日日期（台灣時間）：%s", date_str)

    # 2. 抓取 AI RSS Feed
    logger.info("步驟 2/6：抓取 AI RSS Feed")
    ai_articles = fetch_articles(category="ai")
    if not ai_articles:
        logger.warning("今日沒有抓到任何 AI 新聞，仍會發送通知")

    # 3. Groq API 整理 AI 摘要
    logger.info("步驟 3/6：使用 Groq API 整理 AI 新聞摘要")
    ai_summary = process_news(ai_articles, date_str, category="ai")

    # 4. 抓取資安 RSS Feed
    logger.info("步驟 4/6：抓取資安 RSS Feed")
    security_articles = fetch_articles(category="security")
    if not security_articles:
        logger.warning("今日沒有抓到任何資安新聞，仍會發送通知")

    # 5. Groq API 整理資安摘要
    logger.info("步驟 5/6：使用 Groq API 整理資安新聞摘要")
    security_summary = process_news(security_articles, date_str, category="security")

    # 6. LINE Push Message 發送（兩則分開）
    logger.info("步驟 6/6：透過 LINE 發送訊息")
    send_message(ai_summary)
    send_message(security_summary)

    logger.info("=== 每日新聞彙整完成 ===")


if __name__ == "__main__":
    main()
