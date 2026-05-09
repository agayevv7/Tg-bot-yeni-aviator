import asyncio
from curl_cffi.requests import AsyncSession

async def capture_million_api():
    print("[*] Million.az API Sniper Rejimi Aktivdir...")
    url = "https://www.million.az/auth/signin"
    
    # impersonate="safari_ios_16_0" - Bu, Million.az-ı aldadır ki, 
    # sorğu proqramdan yox, həqiqi iPhone brauzerindən gəlir.
    async with AsyncSession(impersonate="safari_ios_16_0") as s:
        try:
            resp = await s.get(url, timeout=15)
            
            print("\n" + "="*60)
            print(">>> TAPILAN REАL API MƏLUMATLAR:")
            print("="*60)
            
            # 1. KUKILARI TUTURUQ
            cookies = s.cookies.get_dict()
            if cookies:
                for name, value in cookies.items():
                    print(f"[COOKIE] {name}={value}")
            else:
                print("[!] Kuki tapılmadı (Cloudflare bloklaya bilər).")

            # 2. STATUSI YOXLAYIRIQ (200 olmalıdır)
            print(f"\n[STATUS CODE] {resp.status_code}")
            
            if resp.status_code == 200:
                print("\n[MÜVƏFFƏQİYYƏT] API Giriş Qapısı Tapıldı!")
            
            print("="*60)

        except Exception as e:
            print(f"[FATAL] Hədəfə sızmaq mümkün olmadı: {e}")

if __name__ == "__main__":
    asyncio.run(capture_million_api())
