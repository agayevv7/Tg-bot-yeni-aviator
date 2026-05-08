import asyncio
import httpx
import random

TARGET = "https://empro.az" # Hədəf sayt

# Hack üçün ən kritik qovluq və fayl siyahısı (Wordlist)
PATHS = [
    "/admin", "/admin/", "/login", "/administrator", "/wp-login.php", 
    "/cp", "/cpanel", "/webmail", "/config.php", "/config.php.bak",
    "/.env", "/.git/config", "/db.sql", "/database.sql", "/backup.zip",
    "/phpmyadmin", "/sql", "/upload.php", "/shell.php", "/api/v1/user",
    "/server-status", "/info.php", "robots.txt", "/sitemap.xml"
]

async def scan(path, client):
    url = f"{TARGET}{path}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }
    
    try:
        # Cloudflare bypass üçün 5-10 saniyəlik timeout
        response = await client.get(url, headers=headers, follow_redirects=True, timeout=10)
        
        # Əgər status 200 (Uğurlu) və ya 403 (Qadağan amma mövcud) olsa
        if response.status_code == 200:
            print(f"✅ [SUCCESS] Qapı tapıldı: {url} (Status: 200)")
            # Burada 'admin' və ya 'login' sözü keçirsə qeyd et
            if "login" in response.text.lower() or "user" in response.text.lower():
                 print(f"   🚩 [CRITICAL] Bu bir giriş panelidir!")
        
        elif response.status_code == 403:
            print(f"🚫 [FORBIDDEN] {url} (Status: 403) - Qorunur amma orada fayl var!")

    except Exception:
        pass

async def main():
    print(f"🕵️  SIZMA TESTİ ÜÇÜN KƏŞFİYYAT BAŞLADI: {TARGET}")
    print(f"[*] Cəmi {len(PATHS)} kritik nöqtə yoxlanılır...\n")
    
    limits = httpx.Limits(max_connections=20)
    async with httpx.AsyncClient(limits=limits, http2=True, verify=False) as client:
        # Axtarışı sürətləndirmək üçün asinxron işə salırıq
        tasks = [scan(p, client) for p in PATHS]
        await asyncio.gather(*tasks)
    
    print(f"\n[!] Kəşfiyyat bitdi. Tapılan nöqtələr üzərindən sızmağa başlayın.")

if __name__ == "__main__":
    asyncio.run(main())
