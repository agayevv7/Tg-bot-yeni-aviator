import os
import json
import time
import random
import threading
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8756196909:AAHMJ53ExNhnm7ewDR_Gho01C6_g9R4aPL8")
ADMIN_ID = os.environ.get("ADMIN_ID", "2083084323")
PORT = int(os.environ.get("PORT", 5000))
WEBAPP_URL = os.environ.get("WEBAPP_URL", f"https://aviator-bot.up.railway.app")
REFERRAL_LINK = "https://1weucj.life/?open=register&p=mlg1"
SIGNAL_INTERVAL = 120  # 2 dəqiqə

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ─── STATE ────────────────────────────────────────────────────────────────────
active_users = set()
user_data = {}
signal_history = []
current_signal = {"multiplier": 0, "win_rate": 0, "timestamp": "", "countdown": 0}
signal_counter = 0

# ─── KÖMƏKÇİ FUNKSİYALAR ─────────────────────────────────────────────────────

def send_message(chat_id, text, parse_mode="HTML", reply_markup=None):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        logger.error(f"Mesaj göndərmə xətası: {e}")
        return None

def send_photo(chat_id, photo_url, caption="", reply_markup=None):
    url = f"{TELEGRAM_API}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        logger.error(f"Şəkil göndərmə xətası: {e}")
        return None

def edit_message(chat_id, message_id, text, parse_mode="HTML", reply_markup=None):
    url = f"{TELEGRAM_API}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        logger.error(f"Mesaj redaktə xətası: {e}")
        return None

def answer_callback(callback_id, text="", show_alert=False):
    url = f"{TELEGRAM_API}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": show_alert
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Callback cavab xətası: {e}")

def set_webhook():
    webhook_url = f"{WEBAPP_URL}/webhook"
    url = f"{TELEGRAM_API}/setWebhook"
    payload = {"url": webhook_url}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        logger.info(f"Webhook quruldu: {resp.json()}")
        return resp.json()
    except Exception as e:
        logger.error(f"Webhook xətası: {e}")
        return None

# ─── SİQNAL GENERATORU ────────────────────────────────────────────────────────

def generate_signal():
    global signal_counter
    signal_counter += 1
    
    multiplier = round(random.uniform(1.10, 1.25), 2)
    win_rate = random.randint(60, 90)
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    return {
        "id": signal_counter,
        "multiplier": multiplier,
        "win_rate": win_rate,
        "timestamp": timestamp,
        "countdown": SIGNAL_INTERVAL
    }

def broadcast_signal(signal):
    global current_signal, signal_history
    
    current_signal = signal
    signal_history.append(signal)
    if len(signal_history) > 50:
        signal_history = signal_history[-50:]
    
    message_text = (
        f"🎰 <b>AVIATOR SİQNALI</b> 🎰\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📈 <b>Multiplier:</b> <code>{signal['multiplier']}x</code>\n"
        f"✅ <b>Qazanma Faizi:</b> <code>{signal['win_rate']}%</code>\n"
        f"⏰ <b>Vaxt:</b> {signal['timestamp']}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 <a href='{REFERRAL_LINK}'>AVIATOR OYNA</a>\n"
        f"🔄 <i>Növbəti siqnal 2 dəqiqəyə...</i>"
    )
    
    start_button = {
        "inline_keyboard": [[
            {"text": "▶️ SİQNALI BAŞLAT", "callback_data": "start_signals"},
            {"text": "⏹ SİQNALI DAYANDIR", "callback_data": "stop_signals"}
        ], [
            {"text": "📊 STATİSTİKA", "callback_data": "show_stats"},
            {"text": "💰 OYNA", "url": REFERRAL_LINK}
        ]]
    }
    
    for uid in list(active_users):
        try:
            send_message(uid, message_text, reply_markup=start_button)
        except Exception as e:
            logger.error(f"{uid} istifadəçisinə göndərilmədi: {e}")
            active_users.discard(uid)
    
    logger.info(f"Siqnal #{signal['id']} {len(active_users)} istifadəçiyə göndərildi")

def signal_loop():
    while True:
        try:
            signal = generate_signal()
            broadcast_signal(signal)
            
            for remaining in range(SIGNAL_INTERVAL - 1, 0, -10):
                time.sleep(10)
                current_signal["countdown"] = remaining
            
            time.sleep(10)
        except Exception as e:
            logger.error(f"Siqnal dövrü xətası: {e}")
            time.sleep(5)

# ─── BOT ƏMR İŞLƏYİCİLƏRİ ────────────────────────────────────────────────────

def handle_start(chat_id, user_id, username=""):
    user_data[user_id] = {
        "username": username,
        "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "active": True
    }
    active_users.add(user_id)
    
    welcome_text = (
        f"🎮 <b>AVIATOR BOTUNA XOŞ GƏLDİNİZ!</b> 🎮\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👋 <b>İstifadəçi:</b> @{username}\n\n"
        f"✅ <b>İndi siqnalları alırsınız!</b>\n"
        f"📈 Siqnallar hər <b>2 dəqiqədən</b> bir gəlir\n\n"
        f"🔹 <b>Əmrlər:</b>\n"
        f"  /start — Siqnalları başlat\n"
        f"  /stop  — Siqnalları dayandır\n"
        f"  /stats — Statistikaya bax\n"
        f"  /play  — Aviator oyununu aç\n\n"
        f"💰 <a href='{REFERRAL_LINK}'>🎯 İNDİ AVIATOR OYNA</a>"
    )
    
    buttons = {
        "inline_keyboard": [[
            {"text": "▶️ BAŞLAT", "callback_data": "start_signals"},
            {"text": "⏹ DAYANDIR", "callback_data": "stop_signals"}
        ], [
            {"text": "📊 STATİSTİKA", "callback_data": "show_stats"},
            {"text": "💰 OYNA", "url": REFERRAL_LINK}
        ]]
    }
    
    send_message(chat_id, welcome_text, reply_markup=buttons)
    logger.info(f"{user_id} (@{username}) botu başlatdı")

def handle_stop(chat_id, user_id):
    active_users.discard(user_id)
    if user_id in user_data:
        user_data[user_id]["active"] = False
    
    stop_text = (
        f"⏹ <b>SİQNALAR DAYANDIRILDI</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Artıq siqnal qəbul etməyəcəksiniz.\n\n"
        f"▶️ Yenidən başlamaq üçün <b>/start</b> yazın!"
    )
    
    buttons = {
        "inline_keyboard": [[
            {"text": "▶️ YENİDƏN BAŞLAT", "callback_data": "start_signals"}
        ]]
    }
    
    send_message(chat_id, stop_text, reply_markup=buttons)
    logger.info(f"{user_id} istifadəçisi siqnalları dayandırdı")

def handle_stats(chat_id, user_id):
    total_signals = signal_counter
    user_since = user_data.get(user_id, {}).get("joined_at", "Bilinmir")
    is_active = user_id in active_users
    
    stats_text = (
        f"📊 <b>SİZİN STATİSTİKANIZ</b> 📊\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🆔 <b>İstifadəçi ID:</b> <code>{user_id}</code>\n"
        f"📅 <b>Qoşuldu:</b> {user_since}\n"
        f"🔵 <b>Status:</b> {'🟢 Aktiv' if is_active else '🔴 Deaktiv'}\n"
        f"📈 <b>Ümumi Siqnallar:</b> {total_signals}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 <a href='{REFERRAL_LINK}'>AVIATOR OYNA</a>"
    )
    
    buttons = {
        "inline_keyboard": [[
            {"text": "▶️ BAŞLAT" if not is_active else "⏹ DAYANDIR", 
             "callback_data": "start_signals" if not is_active else "stop_signals"}
        ]]
    }
    
    send_message(chat_id, stats_text, reply_markup=buttons)

def handle_play(chat_id):
    play_text = (
        f"💰 <b>AVIATOR OYNA</b> 💰\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Oynamağa başlamaq üçün aşağıya klikləyin!\n\n"
        f"🔥 Böyük uduşlar üçün botun siqnallarından istifadə edin!"
    )
    
    buttons = {
        "inline_keyboard": [[
            {"text": "🎯 İNDİ OYNA", "url": REFERRAL_LINK}
        ]]
    }
    
    send_message(chat_id, play_text, reply_markup=buttons)

def handle_webapp(chat_id, user_id):
    webapp_text = (
        f"🌐 <b>AVIATOR CANLI SİQNALLAR</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Canlı siqnal panelini aşağıdan açın!"
    )
    
    buttons = {
        "inline_keyboard": [[
            {"text": "📡 CANLI PANELİ AÇ", "web_app": {"url": f"{WEBAPP_URL}/app"}}
        ]]
    }
    
    send_message(chat_id, webapp_text, reply_markup=buttons)

# ─── CALLBACK İŞLƏYİCİLƏR ────────────────────────────────────────────────────

def handle_callback(callback_data, chat_id, user_id, message_id, callback_id):
    
    if callback_data == "start_signals":
        active_users.add(user_id)
        if user_id in user_data:
            user_data[user_id]["active"] = True
        
        answer_callback(callback_id, "✅ Siqnallar aktivləşdirildi!", show_alert=False)
        
        if current_signal and current_signal["multiplier"] > 0:
            sig = current_signal
            msg = (
                f"✅ <b>SİQNALLAR YENİDƏN BAŞLADI!</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📈 <b>Cari Siqnal:</b> <code>{sig['multiplier']}x</code>\n"
                f"✅ <b>Qazanma Faizi:</b> <code>{sig['win_rate']}%</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"💰 <a href='{REFERRAL_LINK}'>AVIATOR OYNA</a>"
            )
            buttons = {
                "inline_keyboard": [[
                    {"text": "⏹ DAYANDIR", "callback_data": "stop_signals"},
                    {"text": "📊 STATİSTİKA", "callback_data": "show_stats"}
                ], [
                    {"text": "💰 OYNA", "url": REFERRAL_LINK}
                ]]
            }
            send_message(chat_id, msg, reply_markup=buttons)
        else:
            buttons = {
                "inline_keyboard": [[
                    {"text": "⏹ DAYANDIR", "callback_data": "stop_signals"},
                    {"text": "📊 STATİSTİKA", "callback_data": "show_stats"}
                ], [
                    {"text": "💰 OYNA", "url": REFERRAL_LINK}
                ]]
            }
            send_message(chat_id, "✅ <b>Siqnallar aktivləşdirildi!</b> Növbəti siqnal tezliklə gələcək...", reply_markup=buttons)
        
        logger.info(f"{user_id} istifadəçisi callback ilə siqnalları başlatdı")
    
    elif callback_data == "stop_signals":
        active_users.discard(user_id)
        if user_id in user_data:
            user_data[user_id]["active"] = False
        
        answer_callback(callback_id, "⏹ Siqnallar dayandırıldı", show_alert=False)
        
        stop_msg = (
            f"⏹ <b>SİQNALLAR DAYANDIRILDI</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"Yenidən başlamaq üçün <b>/start</b> yazın və ya aşağıya klikləyin."
        )
        buttons = {
            "inline_keyboard": [[
                {"text": "▶️ YENİDƏN BAŞLAT", "callback_data": "start_signals"}
            ]]
        }
        edit_message(chat_id, message_id, stop_msg, reply_markup=buttons)
        logger.info(f"{user_id} istifadəçisi callback ilə siqnalları dayandırdı")
    
    elif callback_data == "show_stats":
        answer_callback(callback_id, "Statistika yüklənir...", show_alert=False)
        handle_stats(chat_id, user_id)

# ─── WEBHOOK İŞLƏYİCİ ──────────────────────────────────────────────────────────

def handle_webhook_update(update):
    try:
        if "callback_query" in update:
            cb = update["callback_query"]
            callback_id = cb["id"]
            user_id = cb["from"]["id"]
            chat_id = cb["message"]["chat"]["id"]
            message_id = cb["message"]["message_id"]
            callback_data = cb["data"]
            
            handle_callback(callback_data, chat_id, user_id, message_id, callback_id)
            return
        
        if "message" not in update:
            return
        
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        username = msg["from"].get("username", "unknown")
        text = msg.get("text", "")
        
        if text == "/start":
            handle_start(chat_id, user_id, username)
        elif text == "/stop":
            handle_stop(chat_id, user_id)
        elif text == "/stats":
            handle_stats(chat_id, user_id)
        elif text == "/play":
            handle_play(chat_id)
        elif text == "/webapp":
            handle_webapp(chat_id, user_id)
        elif text == "/admin" and str(user_id) == ADMIN_ID:
            admin_msg = (
                f"🔐 <b>ADMIN PANELİ</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"👥 <b>Aktiv İstifadəçilər:</b> {len(active_users)}\n"
                f"📊 <b>Ümumi İstifadəçilər:</b> {len(user_data)}\n"
                f"📈 <b>Göndərilən Siqnallar:</b> {signal_counter}\n"
                f"🟢 <b>Status:</b> İşləyir\n"
                f"━━━━━━━━━━━━━━━\n"
                f"<b>Aktiv İstifadəçilər:</b>\n"
            )
            for uid in list(active_users)[:20]:
                uname = user_data.get(uid, {}).get("username", "unknown")
                admin_msg += f"  • {uid} — @{uname}\n"
            send_message(chat_id, admin_msg)
        else:
            help_text = (
                f"🤖 <b>AVIATOR SİQNAL BOTU</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"<b>Mövcud əmrlər:</b>\n"
                f"  /start — Siqnalları başlat\n"
                f"  /stop  — Siqnalları dayandır\n"
                f"  /stats — Statistikaya bax\n"
                f"  /play  — Aviator oyununu aç\n"
                f"  /webapp — Canlı paneli aç\n"
                f"━━━━━━━━━━━━━━━\n"
                f"💰 <a href='{REFERRAL_LINK}'>AVIATOR OYNA</a>"
            )
            send_message(chat_id, help_text)
            
    except Exception as e:
        logger.error(f"Webhook işləyici xətası: {e}")

# ─── FLASK WEB TƏTBİQİ ──────────────────────────────────────────────────────────

app = Flask(__name__)

WEB_APP_HTML = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Aviator Siqnalları — Canlı</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 50%, #0d0d2b 100%);
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
        }
        .container { max-width: 500px; margin: 0 auto; padding: 16px; }
        
        .header {
            text-align: center;
            padding: 20px 0;
            position: relative;
        }
        .header h1 {
            font-size: 28px;
            background: linear-gradient(90deg, #f7971e, #ffd200);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: none;
            font-weight: 900;
            letter-spacing: 1px;
        }
        .header .subtitle {
            color: #8892b0;
            font-size: 13px;
            margin-top: 4px;
        }
        
        .signal-card {
            background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 30px 20px;
            text-align: center;
            margin: 16px 0;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }
        .signal-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(247,151,30,0.03) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 1; }
        }
        .signal-label {
            font-size: 14px;
            color: #8892b0;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 12px;
            position: relative;
            z-index: 1;
        }
        .multiplier {
            font-size: 72px;
            font-weight: 900;
            background: linear-gradient(135deg, #f7971e, #ffd200);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1;
            margin: 10px 0;
            position: relative;
            z-index: 1;
        }
        .multiplier-suffix {
            font-size: 28px;
            -webkit-text-fill-color: #ffd200;
        }
        .win-rate {
            display: inline-block;
            background: rgba(0,200,83,0.15);
            border: 1px solid rgba(0,200,83,0.3);
            border-radius: 30px;
            padding: 8px 24px;
            font-size: 16px;
            font-weight: 600;
            color: #00c853;
            margin-top: 8px;
            position: relative;
            z-index: 1;
        }
        .signal-time {
            color: #5a6380;
            font-size: 12px;
            margin-top: 16px;
            position: relative;
            z-index: 1;
        }
        
        .countdown-container {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin: 20px 0;
        }
        .countdown-item {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 12px 16px;
            min-width: 70px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.06);
        }
        .countdown-value {
            font-size: 28px;
            font-weight: 700;
            color: #f7971e;
        }
        .countdown-label {
            font-size: 10px;
            color: #5a6380;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 2px;
        }
        
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 16px 0;
        }
        .stat-item {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 16px 10px;
            text-align: center;
        }
        .stat-value {
            font-size: 22px;
            font-weight: 700;
            color: #ffd200;
        }
        .stat-label {
            font-size: 11px;
            color: #5a6380;
            margin-top: 4px;
        }
        
        .history-title {
            font-size: 16px;
            font-weight: 700;
            color: #ccd6f6;
            margin: 20px 0 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .history-table {
            width: 100%;
            border-collapse: collapse;
        }
        .history-table th {
            text-align: left;
            padding: 10px 12px;
            font-size: 11px;
            text-transform: uppercase;
            color: #5a6380;
            letter-spacing: 1px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .history-table td {
            padding: 10px 12px;
            font-size: 14px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            color: #ccd6f6;
        }
        .history-table tr:hover td {
            background: rgba(255,255,255,0.03);
        }
        .badge-win {
            color: #00c853;
            font-weight: 600;
        }
        .badge-multiplier {
            color: #f7971e;
            font-weight: 700;
        }
        
        .play-button {
            display: block;
            background: linear-gradient(135deg, #f7971e, #ffd200);
            color: #0a0e27;
            text-align: center;
            padding: 18px;
            border-radius: 14px;
            font-size: 18px;
            font-weight: 800;
            text-decoration: none;
            margin: 20px 0;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 20px rgba(247,151,30,0.3);
        }
        .play-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 30px rgba(247,151,30,0.5);
        }
        .play-button:active {
            transform: translateY(0);
        }
        
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
            animation: blink 1.5s ease-in-out infinite;
        }
        .status-dot.green { background: #00c853; }
        .status-dot.red { background: #ff1744; }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .footer {
            text-align: center;
            padding: 20px 0;
            color: #3a4370;
            font-size: 12px;
        }
        
        body.telegram {
            background: var(--tg-theme-bg-color, #0a0e27);
        }
        
        @media (max-width: 400px) {
            .multiplier { font-size: 52px; }
            .signal-card { padding: 20px 16px; }
            .stats-bar { grid-template-columns: repeat(3, 1fr); gap: 6px; }
            .countdown-item { min-width: 60px; padding: 10px 12px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✈️ AVIATOR</h1>
            <div class="subtitle">Canlı Siqnal Paneli</div>
        </div>
        
        <div class="signal-card">
            <div class="signal-label">
                <span class="status-dot green" id="statusDot"></span>
                CANLI SİQNAL
            </div>
            <div class="multiplier" id="multiplier">
                ---<span class="multiplier-suffix">x</span>
            </div>
            <div class="win-rate" id="winRate">--- Qazanma Faizi</div>
            <div class="signal-time" id="signalTime">Siqnal gözlənilir...</div>
        </div>
        
        <div class="countdown-container">
            <div class="countdown-item">
                <div class="countdown-value" id="countdownMin">0</div>
                <div class="countdown-label">Dəqiqə</div>
            </div>
            <div class="countdown-item">
                <div class="countdown-value" id="countdownSec">0</div>
                <div class="countdown-label">Saniyə</div>
            </div>
        </div>
        
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-value" id="totalSignals">0</div>
                <div class="stat-label">Ümumi Siqnallar</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="avgMultiplier">0.00</div>
                <div class="stat-label">Orta Multiplier</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="avgWinRate">0%</div>
                <div class="stat-label">Orta Qazanma</div>
            </div>
        </div>
        
        <div class="history-title">📋 Siqnal Tarixçəsi</div>
        <table class="history-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Vaxt</th>
                    <th>Multiplier</th>
                    <th>Qazanma</th>
                </tr>
            </thead>
            <tbody id="historyBody">
                <tr><td colspan="4" style="text-align:center;color:#5a6380;padding:20px;">Siqnallar gözlənilir...</td></tr>
            </tbody>
        </table>
        
        <a class="play-button" href="{{ REFERRAL }}" target="_blank">
            🎯 İNDİ AVIATOR OYNA
        </a>
        
        <div class="footer">
            Aviator Siqnal Botu v2.0 — Avtomatik Canlı Siqnallar
        </div>
    </div>
    
    <script>
        async function fetchData() {
            try {
                const resp = await fetch('/api/status');
                const data = await resp.json();
                
                const multEl = document.getElementById('multiplier');
                if (data.current_signal && data.current_signal.multiplier > 0) {
                    multEl.innerHTML = data.current_signal.multiplier + '<span class="multiplier-suffix">x</span>';
                    document.getElementById('winRate').textContent = data.current_signal.win_rate + '% Qazanma Faizi';
                    document.getElementById('signalTime').textContent = 'Son siqnal: ' + data.current_signal.timestamp;
                }
                
                const cd = data.current_signal ? data.current_signal.countdown : 0;
                document.getElementById('countdownMin').textContent = Math.floor(cd / 60);
                document.getElementById('countdownSec').textContent = cd % 60;
                
                document.getElementById('totalSignals').textContent = data.total_signals || 0;
                if (data.avg_multiplier) document.getElementById('avgMultiplier').textContent = data.avg_multiplier;
                if (data.avg_win_rate) document.getElementById('avgWinRate').textContent = data.avg_win_rate + '%';
                
                const tbody = document.getElementById('historyBody');
                if (data.history && data.history.length > 0) {
                    tbody.innerHTML = data.history.slice(-15).reverse().map(s => 
                        `<tr>
                            <td style="color:#5a6380;">#${s.id}</td>
                            <td>${s.timestamp}</td>
                            <td class="badge-multiplier">${s.multiplier}x</td>
                            <td class="badge-win">${s.win_rate}%</td>
                        </tr>`
                    ).join('');
                }
                
                const dot = document.getElementById('statusDot');
                dot.className = 'status-dot green';
                
            } catch(e) {
                document.getElementById('statusDot').className = 'status-dot red';
                console.error('Fetch error:', e);
            }
        }
        
        fetchData();
        setInterval(fetchData, 3000);
        
        if (window.Telegram && window.Telegram.WebApp) {
            document.body.classList.add('telegram');
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(WEB_APP_HTML, REFERRAL=REFERRAL_LINK)

@app.route('/app')
def webapp():
    return render_template_string(WEB_APP_HTML, REFERRAL=REFERRAL_LINK)

@app.route('/api/status')
def api_status():
    avg_mult = round(sum(s['multiplier'] for s in signal_history) / len(signal_history), 2) if signal_history else 0
    avg_win = round(sum(s['win_rate'] for s in signal_history) / len(signal_history)) if signal_history else 0
    
    return jsonify({
        "current_signal": current_signal,
        "total_signals": signal_counter,
        "active_users": len(active_users),
        "total_users": len(user_data),
        "avg_multiplier": avg_mult,
        "avg_win_rate": avg_win,
        "history": signal_history[-20:]
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if update:
        threading.Thread(target=handle_webhook_update, args=(update,)).start()
    return "OK", 200

@app.route('/health')
def health():
    return jsonify({"status": "ok", "active_users": len(active_users), "signals": signal_counter})

# ─── BAŞLADI ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Aviator Siqnal Botu başladılır...")
    
    set_webhook()
    
    signal_thread = threading.Thread(target=signal_loop, daemon=True)
    signal_thread.start()
    logger.info("Siqnal dövrü başladı")
    
    app.run(host="0.0.0.0", port=PORT)
