#!/usr/bin/env python3
"""
🍪 Actualizar cookies frescas de Suno
"""

import json

def update_cookies():
    """Actualizar con cookies frescas"""
    
    # Cookies frescas proporcionadas por el usuario
    fresh_cookies = "singular_device_id=7fc059fe-34d2-4536-8406-f0b36aa40b7b; ajs_anonymous_id=f0f2cc3c-29fc-4994-b313-c6395f7f01c0; _gcl_au=1.1.967689396.1753245394; _axwrt=24c6944f-367e-4935-93d1-a3a85f8a00dd; _ga=GA1.1.666180024.1753245517; _tt_enable_cookie=1; _ttp=01K0TS71AVG32RZB7XJHY47EVG_.tt.1; afUserId=3882fe9a-09c9-44af-bbf0-2f795576bbe6-p; _fbp=fb.1.1753245523258.766316113280164517; has_logged_in_before=true; __stripe_mid=83485d6a-9536-455a-af6d-a1281884f0ded62e90; _clck=5g3z8b%5E2%5Efyz%5E0%5E2060; AF_SYNC=1758345852539; _gcl_gs=2.1.k1$i1758583235$u42332455; _gcl_aw=GCL.1758583242.Cj0KCQjw58PGBhCkARIsADbDilxMP4uOSqOWzTyOPWvIqhjcJ3Z-WIvibpwrfYJlxpH277SWutUj9n8aAiN6EALw_wcB; __client_uat=1758698843; __client_uat_U9tcbTPE=1758698843; __stripe_sid=ae29cf28-47be-4e9d-b7f7-2d396009e363970f4e; clerk_active_context=sess_338VmGRuxvyTwEwYMO0NYgMZtOI:; ttcsid=1758726322712::qYUzqu1xQvHDUSpoHQX_.265.1758729439206.0; _uetsid=6618fc20927811f0bf1e9b526665403c|uzkp91|2|fzl|0|2084; ttcsid_CT67HURC77UB52N3JFBG=1758726322708::P0r3XE6ppWJPuPLCEH5d.298.1758729439480.0; _uetvid=75e947607c9711f0a0a265429931a928|42vysh|1758729440703|8|1|bat.bing.com/p/conversions/c/v; ax_visitor=%7B%22firstVisitTs%22%3A1753245747787%2C%22lastVisitTs%22%3A1758709867604%2C%22currentVisitStartTs%22%3A1758723934473%2C%22ts%22%3A1758729449303%2C%22visitCount%22%3A256%7D; _ga_7B0KEDD7XP=GS2.1.s1758726322$o306$g1$t1758729452$j46$l0$h0; __session=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg3MzMzNTAsImZ2YSI6WzUxNSwtMV0sImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvY2xlcmtfaWQiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvZW1haWwiOiJzb3lwZXBlamFpbWVzQGdtYWlsLmNvbSIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvcGhvbmUiOm51bGwsImlhdCI6MTc1ODcyOTc1MCwiaXNzIjoiaHR0cHM6Ly9jbGVyay5zdW5vLmNvbSIsImp0aSI6ImY4ZTFhODc4ZmFkZDRhYzUwMTI1IiwibmJmIjoxNzU4NzI5NzQwLCJzaWQiOiJzZXNzXzMzOFZtR1J1eHZ5VHdFd1lNTzBOWWdNWnRPSSIsInN0cyI6ImFjdGl2ZSIsInN1YiI6InVzZXJfMnFwWkhYdVNOU2tLdmVBaGtmekVTMTRkZ1RIIn0.HCN6MozK3Jr1-ZdheGiiroLKckoY3HN5jlRtry57hgxN2AHlclJBG2khBToQ4tvCXHP6NoZNuDrzFmyBFiaONqJMCvo4qgdxQRTXHBixmoXpf8tDwP3QFoNNLelLaRfTSpokgaohVg_Xfw3_yj5ATtxvXrfywCUln4KxvHp_HlXj3yfDFfXhg1W3XBQkZPxNxh-gp4fVl1REUFhkSiZAqg3ZdRJM557dpLmS0yYxbxsG72twQLzu69Anm5IHNz_wdySMQaG8gjUnq01kpovxJbxx629wZJh2dkNBKHpwZZrAke6YNylria6DiLgA2Cygtm90VQq7CyJoTEvvucwUsg; __session_U9tcbTPE=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NTg3MzMzNTAsImZ2YSI6WzUxNSwtMV0sImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvY2xlcmtfaWQiOiJ1c2VyXzJxcFpIWHVTTlNrS3ZlQWhrZnpFUzE0ZGdUSCIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvZW1haWwiOiJzb3lwZXBlamFpbWVzQGdtYWlsLmNvbSIsImh0dHBzOi8vc3Vuby5haS9jbGFpbXMvcGhvbmUiOm51bGwsImlhdCI6MTc1ODcyOTc1MCwiaXNzIjoiaHR0cHM6Ly9jbGVyay5zdW5vLmNvbSIsImp0aSI6ImY4ZTFhODc4ZmFkZDRhYzUwMTI1IiwibmJmIjoxNzU4NzI5NzQwLCJzaWQiOiJzZXNzXzMzOFZtR1J1eHZ5VHdFd1lNTzBOWWdNWnRPSSIsInN0cyI6ImFjdGl2ZSIsInN1YiI6InVzZXJfMnFwWkhYdVNOU2tLdmVBaGtmekVTMTRkZ1RIIn0.HCN6MozK3Jr1-ZdheGiiroLKckoY3HN5jlRtry57hgxN2AHlclJBG2khBToQ4tvCXHP6NoZNuDrzFmyBFiaONqJMCvo4qgdxQRTXHBixmoXpf8tDwP3QFoNNLelLaRfTSpokgaohVg_Xfw3_yj5ATtxvXrfywCUln4KxvHp_HlXj3yfDFfXhg1W3XBQkZPxNxh-gp4fVl1REUFhkSiZAqg3ZdRJM557dpLmS0yYxbxsG72twQLzu69Anm5IHNz_wdySMQaG8gjUnq01kpovxJbxx629wZJh2dkNBKHpwZZrAke6YNylria6DiLgA2Cygtm90VQq7CyJoTEvvucwUsg; _dd_s=aid=ef52d868-270c-482a-93a7-7d3ef02da5ed&rum=0&expire=1758730652708"
    
    try:
        # Leer configuración actual
        with open('suno_accounts_stealth.json', 'r') as f:
            config = json.load(f)
        
        print("🍪 Actualizando cookies frescas...")
        
        # Actualizar cookies de la primera cuenta
        if config['accounts']:
            config['accounts'][0]['cookie'] = fresh_cookies
            config['accounts'][0]['last_used'] = 0
            config['accounts'][0]['success_count'] = 0
            config['accounts'][0]['failure_count'] = 0
            config['accounts'][0]['status'] = 'active'
            config['accounts'][0]['cooldown_until'] = 0
            
            print(f"✅ Cookies actualizadas para: {config['accounts'][0]['email']}")
            print(f"🔑 Session ID: sess_338VmGRuxvyTwEwYMO0NYgMZtOI")
            print(f"📅 Expiración: 1758733350 (válida hasta 2025-09-24)")
        
        # Guardar configuración
        with open('suno_accounts_stealth.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("💾 Configuración guardada exitosamente")
        print("🔄 Reinicia el wrapper para aplicar los cambios")
        
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando cookies: {e}")
        return False

if __name__ == "__main__":
    update_cookies()



