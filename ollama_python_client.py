"""
Ollama Python Client - Improved version using official ollama library
"""
import os
try:
    import ollama
    OLLAMA_LIBRARY_AVAILABLE = True
except ImportError:
    OLLAMA_LIBRARY_AVAILABLE = False
    import requests

class OllamaClient:
    def __init__(self):
        self.ngrok_url = "https://bcea9a8ab0da.ngrok-free.app"
        self.local_url = "http://localhost:11434"
        self.available = False
        self.client = None
        self.model = "llama3.1:8b"
        
        # Try to initialize client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Ollama client with best available URL"""
        
        urls_to_try = [
            os.environ.get("OLLAMA_URL"),
            self.ngrok_url,
            self.local_url
        ]
        
        for url in urls_to_try:
            if not url:
                continue
                
            if OLLAMA_LIBRARY_AVAILABLE:
                try:
                    # Use official ollama library
                    client = ollama.Client(host=url)
                    # Test connection
                    models = client.list()
                    if models:
                        self.client = client
                        self.available = True
                        self.current_url = url
                        print(f"✅ Ollama conectado via biblioteca oficial: {url}")
                        return
                except Exception as e:
                    print(f"⚠️ Error conectando a {url}: {e}")
                    continue
            else:
                # Fallback to requests
                try:
                    response = requests.get(f"{url}/api/tags", timeout=5)
                    if response.status_code == 200:
                        self.current_url = url
                        self.available = True
                        print(f"✅ Ollama conectado via requests: {url}")
                        return
                except Exception as e:
                    print(f"⚠️ Error conectando a {url}: {e}")
                    continue
        
        print("❌ No se pudo conectar a ninguna instancia de Ollama")
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response using Ollama"""
        if not self.available:
            return "AI assistant not available. Please check Ollama connection."
        
        try:
            if OLLAMA_LIBRARY_AVAILABLE and self.client:
                # Use official library
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    options={
                        "temperature": 0.8,
                        "top_p": 0.9
                    }
                )
                
                return response['message']['content']
            else:
                # Fallback to requests
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9
                    }
                }
                
                response = requests.post(
                    f"{self.current_url}/api/generate",
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    return response.json().get("response", "")
                else:
                    return f"Error: {response.status_code}"
                    
        except Exception as e:
            return f"AI Error: {str(e)}"
    
    def test_connection(self) -> dict:
        """Test Ollama connection and return status"""
        test_response = self.generate_response("Test", "Respond with 'OK' if working")
        
        return {
            "available": self.available,
            "url": getattr(self, 'current_url', 'None'),
            "library": "ollama" if OLLAMA_LIBRARY_AVAILABLE else "requests",
            "model": self.model,
            "test_response": test_response[:50] + "..." if len(test_response) > 50 else test_response
        }

# Global instance
ollama_client = OllamaClient()