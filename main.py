import asyncio
from curl_cffi.requests import AsyncSession

# Hər iki ehtimalı (V1 və V2 API yollarını) sınaqdan keçiririk
ENDPOINTS = [
    "/wp-json/contact-api/v1/send-otp",
    "/wp-json/contact-api/v2/auth/send-otp",
    "/index.php?rest_route=/contact-api/v1/send-otp"
]

async def probe_api(phone):
    async with AsyncSession(impersonate="chrome120") as s:
        for ep in ENDPOINTS:
            url = f"https://kontakt.az{ep}"
            data = {"number": phone[-9:], "type": "login"}
            headers = {
                "Referer": "https://kontakt.az/hesabim/",
                "X-Requested-With": "XMLHttpRequest"
            }
            
            try:
                r = await s.post(url, json=data, headers=headers)
                print(f"[*] Trying {ep} -> Status: {r.status_code}")
                if r.status_code == 200:
                    print(f"[!!!] REAL API TAPILDI: {ep}")
                    print(f"Cavab: {r.text}")
                    return ep
            except:
                pass
    return None

if __name__ == "__main__":
    asyncio.run(probe_api("994508880067"))
