#!/usr/bin/env python3
"""
Probar credenciales extraídas del cURL
"""

import requests
import os

# Extraer las cookies importantes del cURL
NEW_COOKIES = "singular_device_id=e02c0392-6f13-47ec-9b0f-505301f45f18; ajs_anonymous_id=745e6aa7-a5cb-4540-a54f-6a5353984beb; _gcl_au=1.1.300206667.1758583584; _axwrt=fcd13b82-2700-4e06-8148-d6dd33979d13; _ga=GA1.1.1435852123.1758583585; _tt_enable_cookie=1; _ttp=01K5SVZYAWAG2N88BHA3KG2SVY_.tt.1; _fbp=fb.1.1758583585218.829290678153674485; _clck=1itjkau%5E2%5Efzj%5E0%5E2091; afUserId=f3700f00-0809-47b7-b769-4fa618d7ccac-p; _clsk=1yddhqd%5E1758583586235%5E1%5E0%5Ey.clarity.ms%2Fcollect; AF_SYNC=1758583586368; __client_uat=1758583610; __client_uat_U9tcbTPE=1758583610; ttcsid=1758583585127::KauxDG0kTFiTBSlbu3zp.1.1758583613681.0; _uetsid=8ea44fc0980b11f0a591374e61049a9c|1ylrwh9|2|fzj|0|2091; _uetvid=8ea47ba0980b11f0993a3df3a8dcaa20|hcljk2|1758583614168|2|1|bat.bing.com/p/conversions/c/o; __stripe_mid=90c34579-4ff2-4bbb-805b-6e252b935ebed9360e; __stripe_sid=c81de682-d1b6-4c98-a543-5273551c4321ab9d4e; ttcsid_CT67HURC77UB52N3JFBG=1758583585126::5LJMsIosujgvbiwDThrP.1.1758583632618.0; hmt_id=49834bb7-0e4f-49bf-864a-66c99de00d8f; __cflb=0H28vk2VKwPbLoawFj9ote4RZxB9Q78vHRtxVMo5rWR; ax_visitor=%7B%22firstVisitTs%22%3A1758583587694%2C%22lastVisitTs%22%3Anull%2C%22currentVisitStartTs%22%3A1758583587694%2C%22ts%22%3A1758583755611%2C%22visitCount%22%3A1%7D; _ga_7B0KEDD7XP=GS2.1.s1758583584$o1$g1$t1758583755$j60$l0$h0"

def test_suno_api_access():
    """Probar si estas cookies dan acceso a Suno API"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Cookie": NEW_COOKIES,
        "Referer": "https://suno.com/",
        "Origin": "https://suno.com"
    }
    
    # Endpoints a probar
    test_endpoints = [
        "https://studio-api.suno.ai/api/billing/info/",
        "https://studio-api.suno.ai/api/session",
        "https://studio-api.suno.ai/api/feed/",
    ]
    
    print("🧪 PROBANDO ACCESO A SUNO API")
    print("=" * 40)
    
    for endpoint in test_endpoints:
        try:
            print(f"\n🔍 Probando: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ ACCESO EXITOSO")
                try:
                    data = response.json()
                    print(f"Respuesta: {str(data)[:200]}...")
                except:
                    print(f"Respuesta: {response.text[:200]}...")
            elif response.status_code == 401:
                print("❌ NO AUTENTICADO")
            elif response.status_code == 403:
                print("⚠️  ACCESO DENEGADO")
            elif response.status_code == 429:
                print("⚠️  RATE LIMITED")
            else:
                print(f"⚠️  Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)
    
    # Buscar session_id en las cookies
    if "__client_uat" in NEW_COOKIES:
        print("✅ Encontrado token de cliente")
    
    if "sess_" in NEW_COOKIES:
        print("✅ Encontrado session_id")
    else:
        print("⚠️  No se encontró session_id (sess_)")
        print("Las cookies pueden ser de usuario no logueado")

if __name__ == "__main__":
    test_suno_api_access()