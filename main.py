import asyncio
import re
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

# --- ANALİZ EDİLƏCƏK HƏDƏF ---
TARGET_URL = "https://kontakt.az/hesabim/" # Hansı saytın API-sini tapmaq istəyirsinizsə onu yazın

async def sniff_api():
    print(f"[*] {TARGET_URL} üzərində API Kəşfiyyatı başladı...")
    
    async with AsyncSession(impersonate="chrome120") as s:
        # 1. Saytın ana səhifəsini oxuyuruq
        resp = await s.get(TARGET_URL)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 2. Bütün JavaScript fayllarını tapırıq
        scripts = [script.get('src') for script in soup.find_all('script') if script.get('src')]
        
        # 3. Şübhəli API yollarını hədəf alan tənzimləmə
        api_patterns = [
            r"/wp-json/[a-zA-Z0-9/-]+", 
            r"/api/v[0-9]+/[a-zA-Z0-9/-]+",
            r"/[a-zA-Z0-9_-]+-api/[a-zA-Z0-9/-]+",
            r"send-otp", r"request-sms", r"login-verify"
        ]

        found_endpoints = set()

        # HTML içində gizli API-ləri axtarırıq
        for pattern in api_patterns:
            matches = re.findall(pattern, resp.text)
            for m in matches:
                found_endpoints.add(m)

        # JS fayllarının içini skan edirik (Əsl API-lər buradadır)
        for js_url in scripts:
            if js_url.startswith('/'):
                js_url = TARGET_URL.split('/')[0] + "//" + TARGET_URL.split('/')[2] + js_url
            
            try:
                js_resp = await s.get(js_url, timeout=10)
                for pattern in api_patterns:
                    matches = re.findall(pattern, js_resp.text)
                    for m in matches:
                        found_endpoints.add(m)
            except:
                continue

        print("\n[!!!] TAPILAN REAL API YOLLARI:")
        for ep in found_endpoints:
            if "otp" in ep.lower() or "sms" in ep.lower() or "verify" in ep.lower():
                print(f" >>> [KRİTİK] {ep}")
            else:
                print(f" [Found] {ep}")

if __name__ == "__main__":
    asyncio.run(sniff_api())
