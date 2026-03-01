"""
LINE Push Message 發送模組
- 使用 LINE Bot SDK v3
- 自動分割超過 5000 字元的訊息
"""
import logging

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    PushMessageRequest,
    TextMessage,
)

from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_MESSAGE_MAX_LENGTH, LINE_USER_ID

logger = logging.getLogger(__name__)


def _split_message(text: str, max_length: int = LINE_MESSAGE_MAX_LENGTH) -> list[str]:
    """
    將長訊息依最大長度切割，在換行符處斷開以保持可讀性。

    Returns:
        list of message strings，每段不超過 max_length 字元
    """
    if len(text) <= max_length:
        return [text]

    parts = []
    current = ""

    for line in text.splitlines(keepends=True):
        if len(current) + len(line) > max_length:
            if current:
                parts.append(current.rstrip())
            current = line
        else:
            current += line

    if current.strip():
        parts.append(current.rstrip())

    return parts if parts else [text[:max_length]]


def send_message(text: str) -> None:
    """
    將文字訊息透過 LINE Push Message API 發送給指定使用者。
    若訊息超過 5000 字元，自動分割成多則訊息依序發送。

    Args:
        text: 要發送的訊息內容
    """
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        parts = _split_message(text)
        logger.info("準備發送 %d 則訊息給 %s", len(parts), LINE_USER_ID)

        for i, part in enumerate(parts, 1):
            logger.info("發送第 %d/%d 則訊息（%d 字元）", i, len(parts), len(part))
            line_bot_api.push_message(
                PushMessageRequest(
                    to=LINE_USER_ID,
                    messages=[TextMessage(text=part)],
                )
            )

    logger.info("LINE 訊息發送完成")
