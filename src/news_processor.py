"""
新聞摘要處理模組
- 使用 Groq API（Llama 3.3 70B）整理、翻譯、摘要
- 輸出固定格式的繁體中文新聞彙整
"""
import logging

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, MAX_ARTICLES_FOR_SUMMARY

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
你是一位專業的 AI 科技新聞編輯，擅長將英文 AI 科技新聞整理成繁體中文摘要。
你的讀者是對 AI 科技有興趣的台灣使用者。
請保持客觀、精確，使用台灣慣用的繁體中文詞彙。
"""

USER_PROMPT_TEMPLATE = """\
以下是今日收集到的 AI 科技新聞列表，請幫我整理成每日新聞彙整，以繁體中文輸出。

【新聞資料】
{articles_text}

【輸出格式要求】
請嚴格按照以下格式輸出，不要加入其他額外說明：

🤖 每日 AI 新聞彙整 {date}

📌 今日重點趨勢
（用 2-3 句話描述今日 AI 新聞的整體趨勢與重點）

━━━━━━━━━━━━━━━
📰 今日精選新聞（共 N 則）
━━━━━━━━━━━━━━━

1️⃣ 【標題】（繁體中文翻譯標題）
📝 （50-80 字的繁體中文摘要，說明這則新聞的重點內容）
🔗 （原文連結）

2️⃣ 【標題】
📝 （摘要）
🔗 （連結）

（依此類推，選取 5-8 則最重要的新聞）

━━━━━━━━━━━━━━━
🔍 資料來源：RSS Feed 自動彙整
"""


def _format_articles_for_prompt(articles: list) -> str:
    """將文章列表格式化為 prompt 輸入文字"""
    lines = []
    for i, article in enumerate(articles, 1):
        lines.append(f"[{i}] 來源：{article['source']}")
        lines.append(f"    標題：{article['title']}")
        if article.get("summary"):
            lines.append(f"    摘要：{article['summary']}")
        lines.append(f"    連結：{article['url']}")
        if article.get("published_at"):
            lines.append(f"    時間：{article['published_at']}")
        lines.append("")
    return "\n".join(lines)


def process_news(articles: list, date_str: str) -> str:
    """
    使用 Groq API 將文章列表整理成繁體中文新聞彙整。

    Args:
        articles: rss_fetcher 回傳的文章列表
        date_str: 日期字串，例如 "2026-03-01"

    Returns:
        格式化的繁體中文新聞彙整字串
    """
    if not articles:
        logger.warning("沒有文章可整理")
        return f"🤖 每日 AI 新聞彙整 {date_str}\n\n今日暫無新 AI 新聞，請明日再試。"

    selected = articles[:MAX_ARTICLES_FOR_SUMMARY]
    logger.info("傳入 Groq 整理的文章數：%d 篇", len(selected))

    articles_text = _format_articles_for_prompt(selected)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        articles_text=articles_text,
        date=date_str,
    )

    client = Groq(api_key=GROQ_API_KEY)

    logger.info("呼叫 Groq API（模型：%s）...", GROQ_MODEL)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2048,
        temperature=0.3,
    )

    result = response.choices[0].message.content.strip()
    logger.info(
        "Groq API 完成，輸入 tokens：%d，輸出 tokens：%d",
        response.usage.prompt_tokens,
        response.usage.completion_tokens,
    )
    return result
