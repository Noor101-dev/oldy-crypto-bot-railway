import os
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, MenuButtonWebApp
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEB_APP_URL = os.environ.get('WEB_APP_URL', 'https://noor101-dev.github.io/Handy/trading-academy.html')

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first = user.first_name if user else 'Trader'

    button = InlineKeyboardButton(
        text='🚀 Open CoinForge Academy',
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    markup = InlineKeyboardMarkup([[button]])

    await update.message.reply_text(
        f'👋 Welcome to *CoinForge*, {first}!\n\n'
        '📈 Live crypto trading sessions with real instructors.\n'
        '🎓 3 batch levels — Starter, Pro & Max.\n'
        '⚡ Real charts. Real setups. No fluff.\n\n'
        'Tap below to open the academy 👇',
        parse_mode='Markdown',
        reply_markup=markup
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '*CoinForge Commands*\n\n'
        '/start — Open the academy\n'
        '/batches — View pricing & batches\n'
        '/live — See live session schedule\n'
        '/help — Show this message',
        parse_mode='Markdown'
    )

async def batches_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    button = InlineKeyboardButton(
        text='💰 View All Batches',
        web_app=WebAppInfo(url=WEB_APP_URL + '#batches')
    )
    await update.message.reply_text(
        '*CoinForge Batches* 💎\n\n'
        '🥉 *Starter* — $9.99/mo\n4 live sessions, basics, community\n\n'
        '🥈 *Pro* — $19.99/mo\n8 sessions, signals, recordings\n\n'
        '🥇 *Max* — $29.99/mo\nUnlimited sessions + 1-on-1 mentoring',
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[button]])
    )

async def live_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    button = InlineKeyboardButton(
        text='📡 Open Live Schedule',
        web_app=WebAppInfo(url=WEB_APP_URL + '#live')
    )
    await update.message.reply_text(
        '*Upcoming Live Sessions* 📡\n\n'
        '🗓 Jun 16 — Altcoin Season Playbook (19:00 UTC)\n'
        '🗓 Jun 18 — Risk Management Deep Dive (18:00 UTC)\n'
        '🗓 Jun 20 — Live Trade Review & Q&A (20:00 UTC)\n\n'
        'Tap below for the full schedule 👇',
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[button]])
    )

async def post_init(app):
    await app.bot.set_my_commands([
        ('start', 'Open CoinForge Academy'),
        ('batches', 'View batch pricing'),
        ('live', 'Live session schedule'),
        ('help', 'Help & commands'),
    ])
    await app.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(text='Open CoinForge', web_app=WebAppInfo(url=WEB_APP_URL))
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('batches', batches_cmd))
    app.add_handler(CommandHandler('live', live_cmd))
    print('CoinForge bot is running...')
    app.run_polling()

if __name__ == '__main__':
    main()
