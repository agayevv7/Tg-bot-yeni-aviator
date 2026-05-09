import urllib.request
import re
import ssl

# --- ANALİZ EDİLƏCƏK SAYT ---
TARGET_URL = "https://kontakt.az/hesabim/" # Bura istədiyin saytı yaz

def sniff():
    print(f"[*] {TARGET_URL} üzərində API kəşfiyyatı başladı...")
    
    # SSL sertifikat yoxlamasını keçirik (Railway üçün)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"
    }

    try:
        # 1. Saytı oxuyuruq
        req = urllib.request.Request(TARGET_URL, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            html = response.read().decode('utf-8')

        # 2. Şübhəli API yollarını tapmaq üçün Regex
        patterns = [
            r'(/wp-json/[a-zA-Z0-9\._\-/]+)',
            r'(/[a-zA-Z0-9\._\-/]+-api/[a-zA-Z0-9\._\-/]+)',
            r'(/api/v[0-9]/[a-zA-Z0-9\._\-/]+)',
            r'(https?://[a-zA-Z0-9\._\-]+/[a-zA-Z0-9\._\-/]*otp[a-zA-Z0-9\._\-/]*)'
        ]

        found = set()
        for p in patterns:
            matches = re.findall(p, html)
            for m in matches:
                found.add(m)

        # 3. JS fayllarını tapırıq
        js_files = re.findall(r'src="([^"]+\.js)"', html)
        for js_url in js_files[:5]:
            if js_url.startswith('/'):
                js_url = TARGET_URL.split('/')[0] + "//" + TARGET_URL.split('/')[2] + js_url
            
            print(f"[*] JS Skan edilir: {js_url[:60]}")
            try:
                js_req = urllib.request.Request(js_url, headers=headers)
                with urllib.request.urlopen(js_req, context=ctx) as js_res:
                    js_code = js_res.read().decode('utf-8')
                    for p in patterns:
                        js_matches = re.findall(p, js_code)
                        for jm in js_matches:
                            found.add(jm)
            except:
                continue

        print("\n" + "="*50)
        print("TAPILAN REAL API YOLLARI:")
        print("="*50)
        for link in sorted(found):
            if any(x in link.lower() for x in ["otp", "sms", "verify", "auth", "login"]):
                print(f" >>> [KRİTİK] {link}")
            else:
                print(f" [Link] {link}")
        print("="*50)

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    sniff()
