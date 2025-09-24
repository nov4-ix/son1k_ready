#!/usr/bin/env python3
"""
🎵 Test de Traducción Ollama-Suno
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_suno_proxy import ollama_suno_proxy

async def test_translation():
    """Test de traducción"""
    
    print("🌐 TEST DE TRADUCCIÓN OLLAMA-SUNO")
    print("=" * 40)
    
    # Configurar credenciales
    ollama_suno_proxy.setup_suno_credentials(
        session_id="f59e657e-9435-4785-9ee1-c6f77fa7081d",
        cookie="singular_device_id=7fc059fe-34d2-4536-8406-f0b36aa40b7b; ajs_anonymous_id=f0f2cc3c-29fc-4994-b313-c6395f7f01c0; _gcl_au=1.1.967689396.1753245394; _axwrt=24c6944f-367e-4935-93d1-a3a85f8a00dd; _ga=GA1.1.666180024.1753245517; _tt_enable_cookie=1; _ttp=01K0TS71AVG32RZB7XJHY47EVG_.tt.1; afUserId=3882fe9a-09c9-44af-bbf0-2f795576bbe6-p; _fbp=fb.1.1753245523258.766316113280164517; has_logged_in_before=true; __stripe_mid=83485d6a-9536-455a-af6d-a1281884f0ded62e90; _clck=5g3z8b%5E2%5Efyz%5E0%5E2060; AF_SYNC=1758345852539; _gcl_gs=2.1.k1$i1758583235$u42332455; _gcl_aw=GCL.1758583242.Cj0KCQjw58PGBhCkARIsADbDilxMP4uOSqOWzTyOPWvIqhjcJ3Z-WIvibpwrfYJlxpH277SWutUj9n8aAiN6EALw_wcB; __client_uat=1758698843; __client_uat_U9tcbTPE=1758698843; clerk_active_context=sess_338VmGRuxvyTwEwYMO0NYgMZtOI:; __session=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg3MDI0NDYsImZ2YSI6WzAsLTFdLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2NsZXJrX2lkIjoidXNlcl8ycXBaSFh1U05Ta0t2ZUFoa2Z6RVMxNGRnVEgiLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2VtYWlsIjoic295cGVwZWphaW1lc0BnbWFpbC5jb20iLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL3Bob25lIjpudWxsLCJpYXQiOjE3NTg2OTg4NDYsImlzcyI6Imh0dHBzOi8vY2xlcmsuc3Vuby5jb20iLCJqdGkiOiIwMjZiNzJiNzFlYjgwM2I0Y2EyMiIsIm5iZiI6MTc1ODY5ODgzNiwic2lkIjoic2Vzc18zMzhWbUdSdXh2eVR3RXdZTU8wTllnTVp0T0kiLCJzdHMiOiJhY3RpdmUiLCJzdWIiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCJ9.EPgJtbVBjEaq3yXlVCWyYf--VyTwKmN4eW4k3dIWqfJEfAA4d7z3KKk0aHBNYHjWEz0tTfq2uq5TIoGv3bBKbd4BlTgKUOSFVfOX_iXGoG-A9iNRmeoWMPiUtzRXvAHsIc2hml16SCvy8k-_kvKNE7x7r6_ZkINNrLvVlTqj7_65R3zHr0xL-APPXmz1rIW23B45zMYJ19uaCzQ4br1J_HK0NIW15DzPFcD9voQ9WVumU1eOYcR2v9NG4Zow3o1PuYx9CiH_POjRHx8KZfNcGbbXzv8SVpZ7YRnGuQ5j5Qbizw3fCyoUJg7V-WNSsRv6isTqvwf_Dl_t5zINot6HVg; __session_U9tcbTPE=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg3MDI0NDYsImZ2YSI6WzAsLTFdLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2NsZXJrX2lkIjoidXNlcl8ycXBaSFh1U05Ta0t2ZUFoa2Z6RVMxNGRnVEgiLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2VtYWlsIjoic295cGVwZWphaW1lc0BnbWFpbC5jb20iLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL3Bob25lIjpudWxsLCJpYXQiOjE3NTg2OTg4NDYsImlzcyI6Imh0dHBzOi8vY2xlcmsuc3Vuby5jb20iLCJqdGkiOiIwMjZiNzJiNzFlYjgwM2I0Y2EyMiIsIm5iZiI6MTc1ODY5ODgzNiwic2lkIjoic2Vzc18zMzhWbUdSdXh2eVR3RXdZTU8wTllnTVp0T0kiLCJzdHMiOiJhY3RpdmUiLCJzdWIiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCJ9.EPgJtbVBjEaq3yXlVCWyYf--VyTwKmN4eW4k3dIWqfJEfAA4d7z3KKk0aHBNYHjWEz0tTfq2uq5TIoGv3bBKbd4BlTgKUOSFVfOX_iXGoG-A9iNRmeoWMPiUtzRXvAHsIc2hml16SCvy8k-_kvKNE7x7r6_ZkINNrLvVlTqj7_65R3zHr0xL-APPXmz1rIW23B45zMYJ19uaCzQ4br1J_HK0NIW15DzPFcD9voQ9WVumU1eOYcR2v9NG4Zow3o1PuYx9CiH_POjRHx8KZfNcGbbXzv8SVpZ7YRnGuQ5j5Qbizw3fCyoUJg7V-WNSsRv6isTqvwf_Dl_t5zINot6HVg; ax_visitor=%7B%22firstVisitTs%22%3A1753245747787%2C%22lastVisitTs%22%3A1758689516087%2C%22currentVisitStartTs%22%3A1758698828659%2C%22ts%22%3A1758698847587%2C%22visitCount%22%3A254%7D; _ga_7B0KEDD7XP=GS2.1.s1758698828$o302$g1$t1758698848$j40$l0$h0; ttcsid=1758698829224::l6XFh2IFxVYhRcO_UzMS.261.1758698848476.0; _uetsid=6618fc20927811f0bf1e9b526665403c|uzkp91|2|fzl|0|2084; ttcsid_CT67HURC77UB52N3JFBG=1758698829223::KzLq3ALldVX6izpEBS2B.294.1758698851575.0; _uetvid=75e947607c9711f0a0a265429931a928|1hcmv6|1758698854306|2|1|bat.bing.com/p/conversions/c/q; __stripe_sid=06bde87b-e58b-44e3-98eb-dac364287c763b711f; _dd_s=aid=ef52d868-270c-482a-93a7-7d3ef02da5ed&rum=0&expire=1758699925576",
        token="eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg3MDI0NDYsImZ2YSI6WzAsLTFdLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2NsZXJrX2lkIjoidXNlcl8ycXBaSFh1U05Ta0t2ZUFoa2Z6RVMxNGRnVEgiLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2VtYWlsIjoic295cGVwZWphaW1lc0BnbWFpbC5jb20iLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL3Bob25lIjpudWxsLCJpYXQiOjE3NTg2OTg4NDYsImlzcyI6Imh0dHBzOi8vY2xlcmsuc3Vuby5jb20iLCJqdGkiOiIwMjZiNzJiNzFlYjgwM2I0Y2EyMiIsIm5iZiI6MTc1ODY5ODgzNiwic2lkIjoic2Vzc18zMzhWbUdSdXh2eVR3RXdZTU8wTllnTVp0T0kiLCJzdHMiOiJhY3RpdmUiLCJzdWIiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCJ9.EPgJtbVBjEaq3yXlVCWyYf--VyTwKmN4eW4k3dIWqfJEfAA4d7z3KKk0aHBNYHjWEz0tTfq2uq5TIoGv3bBKbd4BlTgKUOSFVfOX_iXGoG-A9iNRmeoWMPiUtzRXvAHsIc2hml16SCvy8k-_kvKNE7x7r6_ZkINNrLvVlTqj7_65R3zHr0xL-APPXmz1rIW23B45zMYJ19uaCzQ4br1J_HK0NIW15DzPFcD9voQ9WVumU1eOYcR2v9NG4Zow3o1PuYx9CiH_POjRHx8KZfNcGbbXzv8SVpZ7YRnGuQ5j5Qbizw3fCyoUJg7V-WNSsRv6isTqvwf_Dl_t5zINot6HVg"
    )
    
    # Test de traducción directa
    print("🔍 Probando traducción directa...")
    
    test_prompts = [
        "música rock",
        "canción de amor",
        "música electrónica",
        "balada romántica",
        "música pop"
    ]
    
    for prompt in test_prompts:
        print(f"\n📝 Prompt original: '{prompt}'")
        translated = await ollama_suno_proxy._translate_to_english(prompt)
        print(f"🌐 Traducido: '{translated}'")
    
    # Test de generación completa
    print(f"\n🎵 Probando generación completa...")
    result = await ollama_suno_proxy.generate_music_via_ollama(
        prompt="música rock",
        lyrics="Vamos a rockear esta noche",
        style="rock"
    )
    
    if result["success"]:
        track = result["track"]
        print(f"✅ Generado: {track['title']}")
        print(f"   Prompt original: {track['prompt']}")
        print(f"   Suno prompt: {track['suno_prompt']}")
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_translation())
