"""
RSS Feed 抓取模組
- 從 rss_sources.json 讀取來源
- 過濾 24 小時內的文章
- 依 URL 去重複
- 每來源最多取 N 篇
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import feedparser
from dateutil import parser as dateutil_parser

from config import (
    MAX_ARTICLES_PER_SOURCE,
    NEWS_HOURS_LIMIT,
    RSS_SOURCES_PATH,
)

logger = logging.getLogger(__name__)


def _parse_entry_date(entry: Any) -> Optional[datetime]:
    """從 feedparser entry 中解析發布時間，回傳 timezone-aware datetime 或 None"""
    # feedparser 優先提供 published_parsed 或 updated_parsed（time.struct_time）
    for attr in ("published_parsed", "updated_parsed"):
        time_struct = getattr(entry, attr, None)
        if time_struct:
            try:
                import calendar
                timestamp = calendar.timegm(time_struct)
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            except Exception:
                pass

    # 退而求其次，解析字串格式
    for attr in ("published", "updated"):
        date_str = getattr(entry, attr, None)
        if date_str:
            try:
                dt = dateutil_parser.parse(date_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                pass

    return None


def _get_entry_url(entry: Any) -> str:
    """取得 entry 的 canonical URL"""
    return getattr(entry, "link", "") or getattr(entry, "id", "")


def fetch_articles(category: Optional[str] = None) -> list[dict]:
    """
    從所有啟用的 RSS 來源抓取近 24 小時的新聞。

    Args:
        category: 若指定則只抓取該分類的來源（如 "ai" 或 "security"），None 表示全部

    Returns:
        list of dict with keys: title, url, summary, source, published_at
    """
    if not RSS_SOURCES_PATH.exists():
        raise FileNotFoundError(f"找不到 RSS 來源設定檔：{RSS_SOURCES_PATH}")

    with open(RSS_SOURCES_PATH, encoding="utf-8") as f:
        sources = json.load(f)

    from datetime import timedelta
    cutoff_time = datetime.now(tz=timezone.utc) - timedelta(hours=NEWS_HOURS_LIMIT)

    seen_urls: set[str] = set()
    articles: list[dict] = []

    for source in sources:
        if not source.get("enabled", True):
            continue

        if category and source.get("category") != category:
            continue

        source_name = source.get("name", "Unknown")
        feed_url = source.get("url", "")

        if not feed_url:
            logger.warning("來源 '%s' 缺少 URL，略過", source_name)
            continue

        logger.info("正在抓取：%s", source_name)
        try:
            feed = feedparser.parse(feed_url)
        except Exception as exc:
            logger.error("抓取 '%s' 失敗：%s", source_name, exc)
            continue

        if feed.bozo and feed.bozo_exception:
            logger.warning(
                "來源 '%s' 解析警告：%s", source_name, feed.bozo_exception
            )

        count = 0
        for entry in feed.entries:
            if count >= MAX_ARTICLES_PER_SOURCE:
                break

            url = _get_entry_url(entry)
            if not url or url in seen_urls:
                continue

            published_at = _parse_entry_date(entry)
            if published_at and published_at < cutoff_time:
                continue  # 超過時間範圍，略過

            seen_urls.add(url)
            articles.append(
                {
                    "title": getattr(entry, "title", "（無標題）").strip(),
                    "url": url,
                    "summary": _extract_summary(entry),
                    "source": source_name,
                    "published_at": published_at.isoformat() if published_at else "",
                }
            )
            count += 1

        logger.info("  從 '%s' 取得 %d 篇", source_name, count)

    logger.info("共取得 %d 篇不重複文章", len(articles))
    return articles


def _extract_summary(entry: Any) -> str:
    """從 entry 中提取純文字摘要，限制在 300 字元內"""
    text = ""

    # 優先用 summary，其次 content
    summary = getattr(entry, "summary", "")
    if summary:
        text = summary
    else:
        content_list = getattr(entry, "content", [])
        if content_list:
            text = content_list[0].get("value", "")

    # 簡單去除 HTML 標籤
    import re
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text[:300] if text else ""
