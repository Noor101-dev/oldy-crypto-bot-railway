import os
import random
import requests
import time
from datetime import datetime

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "-1003610983854"
API = f"https://api.telegram.org/bot{TOKEN}"

MEMES = [
    {"url": "https://i.imgflip.com/65939r.jpg", "caption": "Jab BTC 100k pe jaaye 😂🚀\n#HODL #OldyCrypto"},
    {"url": "https://i.imgflip.com/4t0m5.jpg",  "caption": "Mere portfolio ka haal 💀📉\n#Rekt #CryptoLife"},
    {"url": "https://i.imgflip.com/5c7lwq.jpg", "caption": "Buy high sell low 🤡\n#CryptoTrader101"},
    {"url": "https://i.imgflip.com/3oevdk.jpg", "caption": "When you check portfolio at 3am 👀\n#NoSleep"},
    {"url": "https://i.imgflip.com/2zo1ki.jpg", "caption": "Altcoin investors be like 😭\n#Hopium"},
    {"url": "https://i.imgflip.com/26am.jpg",   "caption": "Sab bole DYOR koi nahi karta 🤦\n#DYOR"},
    {"url": "https://i.imgflip.com/1bhk.jpg",   "caption": "Me explaining crypto to my parents 😅"},
    {"url": "https://i.imgflip.com/2wifvo.jpg", "caption": "Diamond hands 💎🙌 Paper hands 🧻\n#HODL"},
]

QUIZ = [
    {"q": "Bitcoin ka maximum supply kitna hai?",    "opts": ["21 Million", "100 Million", "18 Million", "Unlimited"],          "ans": 0, "exp": "Bitcoin ka max supply sirf 21 million hai! 🎯"},
    {"q": "Ethereum kis cheez ke liye famous hai?",  "opts": ["Smart Contracts", "Only Payments", "Mining Gold", "Social"],     "ans": 0, "exp": "Ethereum smart contracts ke liye! 💡"},
    {"q": "What does HODL stand for?",              "opts": ["Hold On for Dear Life", "High Order Data", "Hash Output", "None"],"ans": 0, "exp": "HODL = Hold On for Dear Life! 😂"},
    {"q": "Satoshi Nakamoto ne Bitcoin kab banaya?", "opts": ["2009", "2005", "2012", "2015"],                                   "ans": 0, "exp": "Bitcoin 2009 mein launch hua! 🎂"},
    {"q": "DeFi ka full form kya hai?",             "opts": ["Decentralized Finance", "Digital Finance", "Defined", "Default"], "ans": 0, "exp": "DeFi = Decentralized Finance! 🏦"},
    {"q": "NFT ka full form kya hai?",              "opts": ["Non-Fungible Token", "New Finance Token", "Network Fee", "Node"], "ans": 0, "exp": "NFT = Non-Fungible Token! 🎨"},
    {"q": "Crypto mein whale kaun hota hai?",       "opts": ["Large holder", "A coin type", "Mining rig", "Exchange"],          "ans": 0, "exp": "Whales = log jinke paas bahut saara crypto! 🐋"},
    {"q": "Gas fees kahan pay hoti hai?",           "opts": ["Ethereum network", "Bitcoin", "Binance only", "All chains"],      "ans": 0, "exp": "Gas fees Ethereum transactions ke liye ⛽"},
]

WELCOMES = [
    lambda n: f"🎉 Welcome to OLDY CRYPTO, {n}!\n\n💎 Yahan hum sab HODLers hain\n🚀 Moon tak saath chalenge\n\n✅ No spam  ✅ Respect all  ✅ DYOR\n\nType /meme /quiz /price /profile 🔥",
    lambda n: f"👋 Aagaya {n} bhai!\n\n🔥 OLDY CRYPTO mein swagat hai!\n\n/meme 😂  /quiz 🧠  /price 📊  /profile 👤\n\nDiamond hands rakho! 💎🙌",
    lambda n: f"🌟 {n} joined OLDY CRYPTO family!\n\n₿ Sab ka swagat hai!\n\n📊 /price  🧠 /quiz  😂 /meme  🏆 /leaderboard\n\nLFG! 🚀",
]

leaderboard = {}

def send(text):
    try:
        requests.post(f"{API}/sendMessage", json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"send error: {e}")

def send_photo(url, caption):
    try:
        r = requests.post(f"{API}/sendPhoto", json={"chat_id": CHAT_ID, "photo": url, "caption": caption}, timeout=10)
        if not r.json().get("ok"):
            send(f"{caption}\n{url}")
    except:
        send(f"{caption}\n{url}")

def send_poll(q, opts, ans, exp):
    try:
        requests.post(f"{API}/sendPoll", json={
            "chat_id": CHAT_ID, "question": q, "options": opts,
            "type": "quiz", "correct_option_id": ans,
            "explanation": exp, "is_anonymous": False
        }, timeout=10)
    except Exception as e:
        print(f"poll error: {e}")

def get_prices():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum,binancecoin,solana", "vs_currencies": "usd", "include_24hr_change": "true"}, timeout=10)
        d = r.json()
        lines = []
        for sym, cid in [("BTC","bitcoin"),("ETH","ethereum"),("BNB","binancecoin"),("SOL","solana")]:
            info = d.get(cid, {})
            price = info.get("usd", 0)
            change = info.get("usd_24h_change", 0)
            emoji = "🟢" if change >= 0 else "🔴"
            lines.append(f"{emoji} {sym}: ${price:,.0f} ({change:+.2f}%)")
        return "\n".join(lines)
    except:
        return "🟠 BTC: ~$95,000\n🔵 ETH: ~$3,400\n🟡 BNB: ~$580\n🟣 SOL: ~$170"

def handle(msg):
    chat_id = str(msg.get("chat", {}).get("id", ""))
    if chat_id != CHAT_ID:
        return

    frm = msg.get("from", {})
    uid = str(frm.get("id", ""))
    username = frm.get("username", "")
    first = frm.get("first_name", "")
    last = frm.get("last_name", "")

    if uid:
        if uid not in leaderboard:
            leaderboard[uid] = {"username": username, "name": first, "count": 0}
        leaderboard[uid]["count"] += 1

    for member in msg.get("new_chat_members", []):
        if not member.get("is_bot"):
            name = member.get("first_name") or member.get("username") or "Friend"
            send(random.choice(WELCOMES)(name))
        return

    text = msg.get("text", "").strip()
    cmd = text.split("@")[0].lower()
    print(f"CMD: {cmd} from {username or first}")

    if cmd == "/start":
        send("🤖 Bot is ACTIVE!\n\n⚡ Commands:\n/meme 😂 — Random meme\n/quiz 🧠 — Crypto quiz\n/profile 👤 — Your info\n/price 📊 — Live prices\n/leaderboard 🏆 — Top members\n\nPowered by @Nooraspal 🔥 LFG! 🚀")
    elif cmd == "/meme":
        m = random.choice(MEMES)
        send_photo(m["url"], m["caption"])
    elif cmd == "/quiz":
        q = random.choice(QUIZ)
        send_poll(q["q"], q["opts"], q["ans"], q["exp"])
    elif cmd == "/profile":
        name = " ".join(filter(None, [first, last])) or "Unknown"
        msgs = leaderboard.get(uid, {}).get("count", 0)
        rank = sum(1 for u in leaderboard.values() if u["count"] > msgs) + 1
        send(f"👤 User Profile\n━━━━━━━━━━━━━━\n🏷 Name: {name}\n📛 @{username or 'no_username'}\n🆔 ID: {uid}\n💬 Messages: {msgs}\n🏆 Rank: #{rank}\n━━━━━━━━━━━━━━\n💎 Keep HODLing! 🚀")
    elif cmd == "/price":
        send(f"📊 Live Crypto Prices\n━━━━━━━━━━━━━━\n{get_prices()}\n━━━━━━━━━━━━━━\n⏰ {datetime.utcnow().strftime('%H:%M:%S')} UTC\nSource: CoinGecko")
    elif cmd == "/leaderboard":
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
        lines = [f"{medals[i]} @{u.get('username') or u.get('name','Unknown')} — {u['count']} msgs" for i,(_,u) in enumerate(sorted_lb)] if sorted_lb else ["No activity yet! 💬"]
        send("🏆 OLDY CRYPTO Leaderboard\n━━━━━━━━━━━━━━\n" + "\n".join(lines) + "\n━━━━━━━━━━━━━━\n💎 Most active members!")

def main():
    print("🤖 OLDY CRYPTO Bot started! Listening...")
    offset = None
    while True:
        try:
            params = {"timeout": 30, "allowed_updates": ["message"]}
            if offset:
                params["offset"] = offset
            r = requests.get(f"{API}/getUpdates", params=params, timeout=40)
            updates = r.json().get("result", [])
            for upd in updates:
                offset = upd["update_id"] + 1
                msg = upd.get("message")
                if msg:
                    handle(msg)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
