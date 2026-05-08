import asyncio
import httpx

TARGET = "https://empro.az" # Hədəf sayt
# Tapılmalı olan kritik qovluqlar siyahısı
PATHS = ["/admin", "/login", "/config.php", "/wp-admin", "/shell.php", "/backup", "/db.sql", "/upload"]

async def check_path(url, client):
    try:
        response = await client.get(url)
        if response.status_code == 200:
            print(f"✅ TAPILDI: {url} - Giriş ola bilər!")
        elif response.status_code == 403:
            print(f"🚫 QADAĞAN: {url} - (Amma orada nəsə var)")
    except Exception:
        pass

async def main():
    print(f"🔍 Kəşfiyyat başladı: {TARGET}")
    async with httpx.AsyncClient() as client:
        tasks = [check_path(TARGET + p, client) for p in PATHS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
