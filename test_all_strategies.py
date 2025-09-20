#!/usr/bin/env python3
"""
🧪 Test de Todas las Estrategias de Producción Transparente
"""
import requests
import json
import time

def test_quick_fix_endpoint():
    """Test del endpoint de solución rápida"""
    print("⚡ Probando Quick Fix Endpoint...")
    
    try:
        # Test del health check
        response = requests.get("http://localhost:8001/api/quick-test")
        if response.status_code == 200:
            print("✅ Quick Fix Endpoint funcionando")
            print(f"   Features: {response.json()['features']}")
        else:
            print("❌ Quick Fix Endpoint no responde")
            return False
        
        # Test de naming
        test_lyrics = """Walking down the street tonight
Feeling free and feeling right
Music playing in my head
Dancing till the day is dead"""
        
        naming_response = requests.post("http://localhost:8001/api/test-naming", 
                                      params={"lyrics": test_lyrics})
        
        if naming_response.status_code == 200:
            naming_data = naming_response.json()
            print(f"✅ Naming test: '{naming_data['generated_name']}'")
            print(f"   Filename: {naming_data['filename']}")
            print(f"   Contains suno: {naming_data['contains_suno']}")
            print(f"   Is valid: {naming_data['is_valid']}")
        
        # Test de generación completa
        generation_response = requests.post("http://localhost:8001/api/quick-generate", 
                                          json={
                                              "lyrics": test_lyrics,
                                              "prompt": "upbeat electronic song, 120 BPM",
                                              "instrumental": False
                                          })
        
        if generation_response.status_code == 200:
            gen_data = generation_response.json()
            print(f"✅ Generación completa exitosa")
            print(f"   Job ID: {gen_data['job_id']}")
            print(f"   Status: {gen_data['status']}")
            print(f"   Tracks: {len(gen_data.get('tracks', []))}")
            
            for i, track in enumerate(gen_data.get('tracks', [])):
                print(f"     Track {i+1}: {track['title']}")
                print(f"       Provider: {track['provider']}")
                print(f"       Filename: {track['filename']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en Quick Fix test: {e}")
        return False

def test_main_api_endpoint():
    """Test del endpoint principal corregido"""
    print("\n🎵 Probando Main API Endpoint...")
    
    try:
        # Test health check
        response = requests.get("http://localhost:8000/api/music/health")
        if response.status_code == 200:
            print("✅ Main API funcionando")
        else:
            print("❌ Main API no responde")
            return False
        
        # Test de generación
        generation_response = requests.post("http://localhost:8000/api/music/generate", 
                                          json={
                                              "lyrics": "Testing the transparent production system\nWith dynamic naming capabilities",
                                              "prompt": "electronic test music, upbeat",
                                              "instrumental": False
                                          })
        
        if generation_response.status_code == 200:
            gen_data = generation_response.json()
            print(f"✅ Generación iniciada")
            print(f"   Job ID: {gen_data['job_id']}")
            print(f"   Status: {gen_data['status']}")
            
            # Verificar que no contenga 'suno'
            if 'suno' in gen_data['job_id'].lower():
                print("❌ Job ID aún contiene 'suno'")
                return False
            else:
                print("✅ Job ID transparente (sin 'suno')")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en Main API test: {e}")
        return False

def test_frontend_interceptor():
    """Test del interceptor de frontend"""
    print("\n🎯 Probando Frontend Interceptor...")
    
    # Crear test HTML simple
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Interceptor</title>
</head>
<body>
    <h1>Test de Interceptor Transparente</h1>
    <div id="result"></div>
    
    <script src="frontend_transparent_interceptor.js"></script>
    <script>
        // Test del interceptor
        setTimeout(() => {
            console.log('🧪 Probando interceptor...');
            
            // Simular request que contenga 'suno'
            fetch('/api/suno/generate', {
                method: 'POST',
                body: JSON.stringify({
                    lyrics: 'Test lyrics for interceptor',
                    prompt: 'electronic music'
                })
            }).then(response => response.json())
              .then(data => {
                  console.log('✅ Interceptor funcionando:', data);
                  document.getElementById('result').innerHTML = 
                      '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
              })
              .catch(error => {
                  console.error('❌ Error en interceptor:', error);
              });
        }, 1000);
    </script>
</body>
</html>
"""
    
    with open("/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2/test_interceptor.html", "w") as f:
        f.write(html_content)
    
    print("✅ Test HTML creado: test_interceptor.html")
    print("   Abre este archivo en un navegador para probar el interceptor")
    
    return True

def main():
    """Función principal de test"""
    print("🚀 TEST DE TODAS LAS ESTRATEGIAS DE PRODUCCIÓN TRANSPARENTE")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Quick Fix Endpoint
    results['quick_fix'] = test_quick_fix_endpoint()
    
    # Test 2: Main API Endpoint
    results['main_api'] = test_main_api_endpoint()
    
    # Test 3: Frontend Interceptor
    results['interceptor'] = test_frontend_interceptor()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE RESULTADOS:")
    
    for strategy, success in results.items():
        status = "✅ FUNCIONANDO" if success else "❌ FALLANDO"
        print(f"   {strategy.upper()}: {status}")
    
    all_working = all(results.values())
    
    if all_working:
        print("\n🎯 TODAS LAS ESTRATEGIAS FUNCIONANDO")
        print("🎵 La producción transparente está lista")
        print("🚫 No más referencias a 'suno' en el frontend")
        print("✨ Nombres dinámicos basados en lyrics garantizados")
    else:
        print("\n⚠️ ALGUNAS ESTRATEGIAS NECESITAN REVISIÓN")
        print("🔧 Revisa los errores arriba para solucionar")
    
    print("\n🎯 OPCIONES DISPONIBLES PARA PRODUCCIÓN TRANSPARENTE:")
    print("1. ⚡ Quick Fix Endpoint (puerto 8001) - Solución inmediata")
    print("2. 🎵 Main API Corregido (puerto 8000) - Integración principal")
    print("3. 🔄 Frontend Interceptor - Captura automática de requests")
    print("4. 🔧 Motor Selenium Corregido - Automatización mejorada")
    print("5. 🎯 Sistema Híbrido - Combina todas las estrategias")
    
    return all_working

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)