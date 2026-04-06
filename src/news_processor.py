"""
新聞摘要處理模組
- 使用 Groq API（Llama 3.3 70B）整理、翻譯、摘要
- 輸出固定格式的繁體中文新聞彙整
"""
import logging

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, MAX_ARTICLES_FOR_SUMMARY

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_AI = """\
你是一位專業的 AI 科技新聞編輯，擅長將英文 AI 科技新聞整理成繁體中文摘要。
你的讀者是對 AI 科技有興趣的台灣使用者。
請保持客觀、精確，使用台灣慣用的繁體中文詞彙。
"""

USER_PROMPT_TEMPLATE_AI = """\
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

2️⃣ 【標題】
📝 （摘要）

（依此類推，選取 5-8 則最重要的新聞）

━━━━━━━━━━━━━━━
🔍 資料來源：RSS Feed 自動彙整
"""

SYSTEM_PROMPT_SECURITY = """\
你是一位專業的資訊安全新聞編輯，擅長將英文資安新聞整理成繁體中文摘要。
你的讀者是對資訊安全有興趣的台灣開發者與工程師。
請著重說明漏洞的影響範圍、受影響版本、以及建議的處置方式。
請保持客觀、精確，使用台灣慣用的繁體中文詞彙。
"""

USER_PROMPT_TEMPLATE_SECURITY = """\
以下是今日收集到的資訊安全新聞列表，請幫我整理成每日資安彙整，以繁體中文輸出。

【新聞資料】
{articles_text}

【輸出格式要求】
請嚴格按照以下格式輸出，不要加入其他額外說明：

🔐 每日資安新聞彙整 {date}

⚠️ 今日重點威脅
（用 2-3 句話描述今日資安新聞的整體趨勢與重點威脅）

━━━━━━━━━━━━━━━
🛡️ 今日精選資安新聞（共 N 則）
━━━━━━━━━━━━━━━

1️⃣ 【標題】（繁體中文翻譯標題）
📝 （50-80 字的繁體中文摘要，說明漏洞影響範圍、受影響版本及建議處置）

2️⃣ 【標題】
📝 （摘要）

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


def process_news(articles: list, date_str: str, category: str = "ai") -> str:
    """
    使用 Groq API 將文章列表整理成繁體中文新聞彙整。

    Args:
        articles: rss_fetcher 回傳的文章列表
        date_str: 日期字串，例如 "2026-03-01"
        category: "ai" 或 "security"，決定使用的 prompt 風格

    Returns:
        格式化的繁體中文新聞彙整字串
    """
    if category == "security":
        system_prompt = SYSTEM_PROMPT_SECURITY
        user_prompt_template = USER_PROMPT_TEMPLATE_SECURITY
        empty_msg = f"🔐 每日資安新聞彙整 {date_str}\n\n今日暫無新資安新聞，請明日再試。"
    else:
        system_prompt = SYSTEM_PROMPT_AI
        user_prompt_template = USER_PROMPT_TEMPLATE_AI
        empty_msg = f"🤖 每日 AI 新聞彙整 {date_str}\n\n今日暫無新 AI 新聞，請明日再試。"

    if not articles:
        logger.warning("沒有文章可整理")
        return empty_msg

    selected = articles[:MAX_ARTICLES_FOR_SUMMARY]
    logger.info("傳入 Groq 整理的文章數：%d 篇", len(selected))

    articles_text = _format_articles_for_prompt(selected)
    user_prompt = user_prompt_template.format(
        articles_text=articles_text,
        date=date_str,
    )

    client = Groq(api_key=GROQ_API_KEY)

    logger.info("呼叫 Groq API（模型：%s）...", GROQ_MODEL)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
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
