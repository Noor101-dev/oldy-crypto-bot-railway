import os
import asyncio
import hashlib
import time
import uuid
import httpx
from datetime import datetime
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEB_APP_URL = os.environ.get('WEB_APP_URL', 'https://noor101-dev.github.io/Handy/trading-academy.html')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
TRON_WALLET = os.environ.get('TRON_WALLET', 'TTLMvEwYt8SLRGwBFz1KF9K31PhjbL8P1Q')
ADMIN_IDS = [7647536292, 6416423386]

BATCH_PRICES = {'starter': 9.99, 'pro': 19.99, 'max': 29.99}

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

async def sb_get(table, params=''):
    async with httpx.AsyncClient() as c:
        r = await c.get(f'{SUPABASE_URL}/rest/v1/{table}?{params}', headers=HEADERS)
        return r.json()

async def sb_post(table, data):
    async with httpx.AsyncClient() as c:
        r = await c.post(f'{SUPABASE_URL}/rest/v1/{table}', headers={**HEADERS, 'Prefer': 'return=representation'}, json=data)
        return r.json()

async def sb_patch(table, params, data):
    async with httpx.AsyncClient() as c:
        r = await c.patch(f'{SUPABASE_URL}/rest/v1/{table}?{params}', headers={**HEADERS, 'Prefer': 'return=representation'}, json=data)
        return r.json()

def gen_ref_code(tg_id):
    return hashlib.md5(str(tg_id).encode()).hexdigest()[:8].upper()

async def get_user(tg_id):
    res = await sb_get('users', f'telegram_id=eq.{tg_id}')
    return res[0] if res else None

async def check_tron_payment(expected_amount_usdt, minutes=60):
    try:
        contract = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'
        async with httpx.AsyncClient() as c:
            r = await c.get(
                f'https://api.trongrid.io/v1/accounts/{TRON_WALLET}/transactions/trc20',
                params={'limit': 20, 'contract_address': contract},
                timeout=10
            )
            txs = r.json().get('data', [])
        now = int(time.time() * 1000)
        window = minutes * 60 * 1000
        amount_sun = int(expected_amount_usdt * 1_000_000)
        for tx in txs:
            ts = tx.get('block_timestamp', 0)
            val = int(tx.get('value', 0))
            to = tx.get('to', '')
            if to.lower() == TRON_WALLET.lower() and abs(val - amount_sun) <= 10000 and (now - ts) < window:
                return tx.get('transaction_id')
    except Exception as e:
        print(f'Tron check error: {e}')
    return None

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    first = update.effective_user.first_name or 'Trader'
    ref_by = ctx.args[0] if ctx.args else None
    user = await get_user(tg_id)
    if not user:
        ref_code = gen_ref_code(tg_id)
        await sb_post('users', {
            'telegram_id': tg_id, 'first_name': first,
            'ref_code': ref_code, 'referred_by': ref_by,
            'batch': None, 'batch_active': False,
            'referral_count': 0, 'joined_at': datetime.utcnow().isoformat()
        })
    btn = InlineKeyboardButton('🚀 Open CoinForge Academy', web_app=WebAppInfo(url=WEB_APP_URL))
    await update.message.reply_text(
        f'👋 Welcome to *CoinForge*, {first}!\n\n'
        '📈 Live crypto trading sessions with real instructors.\n'
        '🎓 3 batch levels — Starter, Pro & Max.\n'
        '⚡ Real charts. Real setups. No fluff.\n\n'
        'Tap below to open the academy 👇',
        parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[btn]])
    )

async def pay(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    if not ctx.args:
        await update.message.reply_text('Usage: /pay starter | /pay pro | /pay max')
        return
    batch = ctx.args[0].lower()
    if batch not in BATCH_PRICES:
        await update.message.reply_text('Invalid batch. Choose: starter, pro or max')
        return
    user = await get_user(tg_id)
    price = BATCH_PRICES[batch]
    discount = 0
    ref_by = user.get('referred_by') if user else None
    if ref_by:
        referrer = await sb_get('users', f'ref_code=eq.{ref_by}')
        if referrer and referrer[0].get('referral_count', 0) >= 2:
            discount = round(price * 0.10, 2)
            price = round(price - discount, 2)
    pay_id = str(uuid.uuid4())[:8].upper()
    await sb_post('payments', {
        'pay_id': pay_id, 'telegram_id': tg_id, 'batch': batch,
        'amount': price, 'status': 'pending', 'created_at': datetime.utcnow().isoformat()
    })
    disc_text = f'\n🎉 *10% referral discount applied!* You save ${discount}' if discount else ''
    await update.message.reply_text(
        f'💳 *Payment Instructions*{disc_text}\n\n'
        f'Batch: *{batch.title()}*\n'
        f'Amount: *{price} USDT* (TRC20)\n\n'
        f'Send exactly *{price} USDT* to:\n'
        f'`{TRON_WALLET}`\n\n'
        f'⚠️ TRC20 network only\n'
        f'Payment ID: `{pay_id}`\n\n'
        f'After sending, type /confirm {pay_id}',
        parse_mode='Markdown'
    )

async def confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    if not ctx.args:
        await update.message.reply_text('Usage: /confirm YOUR_PAYMENT_ID')
        return
    pay_id = ctx.args[0].upper()
    payments = await sb_get('payments', f'pay_id=eq.{pay_id}&telegram_id=eq.{tg_id}&status=eq.pending')
    if not payments:
        await update.message.reply_text('Payment not found or already confirmed.')
        return
    payment = payments[0]
    amount = payment['amount']
    batch = payment['batch']
    await update.message.reply_text('🔍 Checking blockchain... please wait.')
    tx_id = await check_tron_payment(amount, minutes=60)
    if tx_id:
        await sb_patch('payments', f'pay_id=eq.{pay_id}', {'status': 'confirmed', 'tx_id': tx_id})
        await sb_patch('users', f'telegram_id=eq.{tg_id}', {
            'batch': batch, 'batch_active': True, 'activated_at': datetime.utcnow().isoformat()
        })
        user = await get_user(tg_id)
        if user and user.get('referred_by'):
            ref_users = await sb_get('users', f'ref_code=eq.{user["referred_by"]}')
            if ref_users:
                new_count = ref_users[0].get('referral_count', 0) + 1
                await sb_patch('users', f'ref_code=eq.{user["referred_by"]}', {'referral_count': new_count})
        await update.message.reply_text(
            f'✅ *Payment Confirmed!*\n\nWelcome to CoinForge *{batch.title()}* batch!\n'
            f'TX: `{tx_id[:24]}...`\n\nYou now have full access 👇',
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🚀 Open CoinForge', web_app=WebAppInfo(url=WEB_APP_URL))]])
        )
    else:
        await update.message.reply_text(
            f'⏳ Payment not detected yet.\n\nMake sure you sent the exact amount on TRC20.\nTry again in 5 min with /confirm {pay_id}'
        )

async def refer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    user = await get_user(tg_id)
    if not user:
        await update.message.reply_text('Please /start first.')
        return
    ref_code = user.get('ref_code', gen_ref_code(tg_id))
    ref_link = f'https://t.me/NOORSMANAGERBOT?start={ref_code}'
    count = user.get('referral_count', 0)
    needed = max(0, 2 - count)
    status = '✅ 10% discount unlocked for the next person who uses your link!' if count >= 2 else f'Refer {needed} more person(s) to unlock 10% discount for them.'
    await update.message.reply_text(
        f'🔗 *Your Referral Link*\n\n`{ref_link}`\n\n'
        f'👥 Referrals: *{count}/2*\n{status}\n\n'
        f'When 2 people join through your link, the next joiner gets 10% off their first payment.',
        parse_mode='Markdown'
    )

async def mybatch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    user = await get_user(tg_id)
    if not user or not user.get('batch_active'):
        await update.message.reply_text('❌ No active batch.\n\nUse /pay starter, /pay pro or /pay max to join.')
        return
    batch = user['batch'].title()
    await update.message.reply_text(
        f'✅ *Active Batch: {batch}*\n\nYou have full access. Open below 👇',
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🚀 Open CoinForge', web_app=WebAppInfo(url=WEB_APP_URL))]])
    )

async def admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    users = await sb_get('users', 'order=joined_at.desc&limit=200')
    total = len(users)
    active = sum(1 for u in users if u.get('batch_active'))
    starters = sum(1 for u in users if u.get('batch') == 'starter')
    pros = sum(1 for u in users if u.get('batch') == 'pro')
    maxs = sum(1 for u in users if u.get('batch') == 'max')
    payments = await sb_get('payments', 'status=eq.confirmed')
    revenue = sum(p.get('amount', 0) for p in payments)
    await update.message.reply_text(
        f'📊 *CoinForge Admin*\n\n'
        f'👥 Total Users: *{total}*\n'
        f'✅ Active: *{active}*\n\n'
        f'🥉 Starter: *{starters}*\n'
        f'🥈 Pro: *{pros}*\n'
        f'🥇 Max: *{maxs}*\n\n'
        f'💰 Revenue: *${revenue:.2f} USDT*\n\n'
        f'/members — list members\n'
        f'/broadcast msg — message all\n'
        f'/remind session — send reminder',
        parse_mode='Markdown'
    )

async def members(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    users = await sb_get('users', 'batch_active=eq.true&order=activated_at.desc')
    if not users:
        await update.message.reply_text('No active members yet.')
        return
    lines = [f'• {u.get("first_name","?")} — {u.get("batch","?").title()} ({u["telegram_id"]})' for u in users[:30]]
    await update.message.reply_text(f'👥 *Active Members ({len(users)})*\n\n' + '\n'.join(lines), parse_mode='Markdown')

async def broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not ctx.args:
        await update.message.reply_text('Usage: /broadcast Your message here')
        return
    msg = ' '.join(ctx.args)
    users = await sb_get('users', 'batch_active=eq.true')
    sent = 0
    for u in users:
        try:
            await ctx.bot.send_message(u['telegram_id'], f'📢 *CoinForge*\n\n{msg}', parse_mode='Markdown')
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await update.message.reply_text(f'✅ Sent to {sent} members.')

async def remind(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not ctx.args:
        await update.message.reply_text('Usage: /remind Session title here')
        return
    session = ' '.join(ctx.args)
    users = await sb_get('users', 'batch_active=eq.true')
    sent = 0
    for u in users:
        try:
            await ctx.bot.send_message(
                u['telegram_id'],
                f'🔔 *Live Session Starting Soon!*\n\n📡 *{session}*\n\nOpen CoinForge to join 👇',
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📡 Join Session', web_app=WebAppInfo(url=WEB_APP_URL))]])
            )
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await update.message.reply_text(f'✅ Reminder sent to {sent} members.')

async def post_init(app: Application):
    await app.bot.set_my_commands([
        ('start', 'Open CoinForge Academy'),
        ('pay', 'Pay for a batch'),
        ('confirm', 'Confirm your payment'),
        ('mybatch', 'Check your active batch'),
        ('refer', 'Get your referral link'),
        ('help', 'Help & commands'),
    ])
    await app.bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text='Open CoinForge', web_app=WebAppInfo(url=WEB_APP_URL)))

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    for cmd, fn in [('start',start),('pay',pay),('confirm',confirm),('refer',refer),('mybatch',mybatch),('admin',admin),('members',members),('broadcast',broadcast),('remind',remind)]:
        app.add_handler(CommandHandler(cmd, fn))
    print('CoinForge bot is running...')
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
