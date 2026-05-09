import urllib.request
import ssl
import re

def get_million_secrets():
    print("[*] Million.az API Kəşfiyyatı Başladı...")
    url = "https://www.million.az/auth/signin"
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as resp:
            # 1. Saytın bizə verdiyi COOKIE-ni tuturuq
            cookies = resp.info().get_all('Set-Cookie')
            print("\n" + "="*50)
            print("TAPILAN REAL KUKİLƏR (BUNLARI MƏNƏ DE):")
            for c in cookies:
                print(f" >>> {c.split(';')[0]}")
            
            # 2. HTML içindən XSRF Tokeni tapırıq
            html = resp.read().decode('utf-8')
            token = re.search(r'name="csrf-token" content="([^"]+)"', html)
            if token:
                print(f"\n >>> X-XSRF-TOKEN: {token.group(1)}")
            print("="*50)
            
    except Exception as e:
        print(f"[!] Xəta: {e}")

if __name__ == "__main__":
    get_million_secrets()
