import asyncio
import re
import random
from curl_cffi.requests import AsyncSession

# --- ANALİZ EDİLƏCƏK SAYT ---
TARGET_URL = "https://kontakt.az/hesabim/" # Bura hansı saytı istəyirsən onu yaz

async def sniff_api():
    print(f"[*] {TARGET_URL} üzərində API Kəşfiyyatı başladı...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
        "Accept": "*/*"
    }

    async with AsyncSession(impersonate="chrome110") as s:
        try:
            # 1. Saytı oxuyuruq
            resp = await s.get(TARGET_URL, headers=headers, timeout=15)
            html_content = resp.text
            
            # 2. Şübhəli API yollarını tapan Regex (Süzgəc)
            # Bu süzgəc bütün gizli linkləri tapacaq
            patterns = [
                r'/[a-zA-Z0-9\._\-/]+-api/[a-zA-Z0-9\._\-/]+',
                r'/wp-json/[a-zA-Z0-9\._\-/]+',
                r'/api/v[0-9]/[a-zA-Z0-9\._\-/]+',
                r'https?://[a-zA-Z0-9\._\-]+/[a-zA-Z0-9\._\-/]*otp[a-zA-Z0-9\._\-/]*',
                r'https?://[a-zA-Z0-9\._\-]+/[a-zA-Z0-9\._\-/]*sms[a-zA-Z0-9\._\-/]*'
            ]

            found_endpoints = set()
            for p in patterns:
                matches = re.findall(p, html_content)
                for m in matches:
                    found_endpoints.add(m)

            # 3. Tapılan JS fayllarını tapıb onların da içini skan edirik
            js_files = re.findall(r'src="([^"]+\.js)"', html_content)
            
            for js_link in js_files[:5]: # İlk 5 əsas JS faylına baxırıq
                if js_link.startswith('/'):
                    js_link = TARGET_URL.split('/')[0] + "//" + TARGET_URL.split('/')[2] + js_link
                
                print(f"[*] JS faylı skan edilir: {js_link[:50]}...")
                try:
                    js_resp = await s.get(js_link, timeout=10)
                    for p in patterns:
                        matches = re.findall(p, js_resp.text)
                        for m in matches:
                            found_endpoints.add(m)
                except:
                    continue

            print("\n" + "="*40)
            print("[!!!] TAPILAN REAL API YOLLARI:")
            print("="*40)
            
            critical_found = False
            for ep in sorted(found_endpoints):
                # Əgər linkin içində otp, sms, auth, login varsa, bu bizim hədəfimizdir
                if any(x in ep.lower() for x in ["otp", "sms", "auth", "login", "verify", "register"]):
                    print(f" >>> [KRİTİK] {ep}")
                    critical_found = True
                else:
                    print(f" [Link] {ep}")
            
            if not critical_found:
                print("\n[!] Dəqiq OTP yolu tapılmadı, başqa alt səhifəni (məsələn /registration) yoxlayın.")
            
            print("="*40)

        except Exception as e:
            print(f"[ERROR] Səhv: {e}")

if __name__ == "__main__":
    asyncio.run(sniff_api())
