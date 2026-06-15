# CoinForge Bot — Railway Deployment

## Files
- `coinforge_bot.py` — Main bot backend
- `requirements_coinforge.txt` — Python dependencies
- `Procfile_coinforge` — Railway start command

## Deploy on Railway (Free)

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project → Deploy from GitHub repo**
3. Select this repo: `oldy-crypto-bot-railway`
4. Set the **Start Command** to: `python coinforge_bot.py`
5. Go to **Variables** tab and add:
   - `BOT_TOKEN` = your token from @BotFather
   - `WEB_APP_URL` = your hosted HTML URL (e.g. GitHub Pages URL)
6. Click **Deploy** — done!

## Environment Variables

| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | From @BotFather |
| `WEB_APP_URL` | Your trading-academy.html URL |

## Commands the bot responds to
- `/start` — Opens the mini app with a button
- `/batches` — Shows pricing
- `/live` — Shows session schedule
- `/help` — Lists commands

## After deploying
The bot will also set a **menu button** so users see "Open CoinForge" right in the chat bar automatically.
