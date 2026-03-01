# 每日 AI 新聞彙整 LINE Bot

每天早上 8:00（台灣時間）自動從多個 AI 科技媒體抓取新聞，透過 Groq AI 整理成繁體中文摘要，推播到 LINE。

## 功能

- 自動抓取 6 個 AI 科技 RSS Feed（24 小時內新聞）
- 使用 Groq API（Llama 3.3 70B）整理、翻譯、摘要
- 透過 LINE Messaging API 推播給指定使用者
- 每天台灣時間 08:00 自動執行（GitHub Actions）

## 技術架構

```
GitHub Actions（每天 UTC 00:00）
    ↓
rss_fetcher.py  →  抓取 RSS、過濾 24h 內新聞、去重複
    ↓
news_processor.py  →  Groq API 整理摘要（繁體中文）
    ↓
line_sender.py  →  LINE Push Message 發送
```

## RSS 來源

| 來源 | 說明 |
|---|---|
| TechCrunch AI | AI 新創、產品新聞 |
| VentureBeat AI | AI 商業應用 |
| MIT Technology Review | AI 學術與趨勢 |
| The Verge AI | AI 科技評論 |
| Google AI Blog | Google 官方 AI 公告 |
| Hugging Face Blog | 開源 AI 模型與工具 |

## 環境變數

複製 `.env.example` 為 `.env` 並填入：

```bash
cp .env.example .env
```

| 變數 | 說明 | 取得位置 |
|---|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot 推播 Token | [LINE Developers Console](https://developers.line.biz/) |
| `LINE_USER_ID` | 接收訊息的 LINE User ID | LINE Developers Console |
| `GROQ_API_KEY` | Groq API 金鑰 | [Groq Console](https://console.groq.com/) |

## 本機執行

```bash
pip install -r requirements.txt
export $(cat .env | xargs)
python main.py
```

## GitHub Actions 設定

在 Repo 的 **Settings → Secrets and variables → Actions** 新增三個 Secrets：

- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_USER_ID`
- `GROQ_API_KEY`

設定完成後，可到 **Actions → Daily AI News → Run workflow** 手動測試。

## 費用

| 服務 | 費用 |
|---|---|
| Groq API | 免費（每天 14,400 次請求）|
| LINE Bot | 免費（每月 200 則，只用 ~30 則）|
| GitHub Actions | 免費（每月 2,000 分鐘，只用 ~60 分鐘）|
