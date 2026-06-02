"""
my-world 新聞推送模組
- 將每日摘要推送到 my-world backend API 存檔
"""
import json
import logging
import urllib.error
import urllib.request

from config import MY_WORLD_API_URL, MY_WORLD_NEWS_API_KEY

logger = logging.getLogger(__name__)


def push_news(content: str, date_str: str, category: str) -> None:
    """
    將新聞摘要推送到 my-world backend。

    Args:
        content: 格式化的摘要字串
        date_str: 日期字串，例如 "2026-06-02"
        category: "ai" 或 "security"
    """
    if not MY_WORLD_API_URL or not MY_WORLD_NEWS_API_KEY:
        logger.warning("MY_WORLD_API_URL 或 MY_WORLD_NEWS_API_KEY 未設定，跳過推送")
        return

    url = f"{MY_WORLD_API_URL.rstrip('/')}/api/news"
    payload = json.dumps({
        "category": category,
        "content": content,
        "date": date_str,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": MY_WORLD_NEWS_API_KEY,
            "User-Agent": "ai-news-linebot/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            logger.info("my-world 推送成功（%s）：HTTP %d", category, resp.status)
    except urllib.error.HTTPError as e:
        logger.error("my-world 推送失敗（%s）：HTTP %d %s", category, e.code, e.reason)
    except Exception as e:
        logger.error("my-world 推送失敗（%s）：%s", category, e)
