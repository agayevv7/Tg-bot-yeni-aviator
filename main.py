import urllib.request
import re
import ssl
import time

# --- ANALİZ EDİLƏCƏK HƏDƏF SAYT ---
# Bura yoxlamaq istədiyin saytın nömrə yazılan səhifəsini yaz
TARGETS = [
    "https://umico.az",
    "https://kontakt.az/hesabim/",
    "https://bakuelectronics.az",
    "https://alipasha.az"
]

def sniff_api(url):
    print(f"\n[!] KƏŞFİYYAT BAŞLADI: {url}")
    
    # SSL və Header ayarlari
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}

    try:
        # 1. Ana səhifəni oxu
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        # 2. JS fayllarını tap
        js_files = re.findall(r'src="([^"]+\.js)"', html)
        
        # 3. API yolları üçün dərindən axtarış regexləri
        patterns = [
            r'(/api/v[0-9]/[a-zA-Z0-9\._\-/]+)',
            r'(/wp-json/[a-zA-Z0-9\._\-/]+)',
            r'([a-zA-Z0-9\._\-/]+-api/[a-zA-Z0-9\._\-/]+)',
            r'(/[a-zA-Z0-9\._\-/]*/sms/[a-zA-Z0-9\._\-/]*)',
            r'(/[a-zA-Z0-9\._\-/]*/otp/[a-zA-Z0-9\._\-/]*)'
        ]

        found_endpoints = set()

        # HTML içində axtar
        for p in patterns:
            for m in re.findall(p, html):
                found_endpoints.add(m)

        # JS fayllarının içində dərindən axtar (Əsas API-lər buradadır)
        for js in js_files[:10]: # İlk 10 əsas JS faylı
            if js.startswith('/'):
                js = url.split('/')[0] + "//" + url.split('/')[2] + js
            elif not js.startswith('http'):
                continue
                
            try:
                js_req = urllib.request.Request(js, headers=headers)
                with urllib.request.urlopen(js_req, context=ctx, timeout=10) as js_resp:
                    js_code = js_resp.read().decode('utf-8', errors='ignore')
                    for p in patterns:
                        for m in re.findall(p, js_code):
                            found_endpoints.add(m)
            except:
                continue

        # Nəticələri filtrələ və göstər
        print("-" * 50)
        print(f"RESULT FOR {url}:")
        critical_found = False
        for ep in sorted(found_endpoints):
            low_ep = ep.lower()
            if any(k in low_ep for k in ["otp", "sms", "login", "auth", "verify", "register"]):
                print(f" >>> [KRİTİK API] {ep}")
                critical_found = True
            else:
                # Çox uzun lazımsız linkləri gizlədirik
                if len(ep) < 60:
                    print(f" [Link] {ep}")
        
        if not critical_found:
            print("[?] Bu səhifədə birbaşa OTP yolu tapılmadı.")
        print("-" * 50)

    except Exception as e:
        print(f"[ERROR] {url} skan edilərkən xəta: {e}")

if __name__ == "__main__":
    for t in TARGETS:
        sniff_api(t)
        time.sleep(2)
