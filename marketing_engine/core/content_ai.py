import os
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class ContentAI:
    """
    Cerebro del Bot NeuralJira utilizando Google Gemini 1.5.
    Implementación vía REST para evitar problemas de dependencias.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = "gemini-2.5-flash"
    
    def generate_post_content(self, raw_input: str, template_type: str = "tutorial") -> Dict[str, Any]:
        if not self.api_key: return {}

        # Generar prompt según el template
        system_prompt = "Eres un estratega de marketing cyberpunk. Responde SOLO JSON."
        user_prompt = f"Genera un JSON para el template {template_type} basado en: {raw_input}. Esquema: {{'title': '...', 'steps': [], 'cta': '...'}} si es tutorial, o {{'headline': '...', 'body': '...', 'source': '...'}} si es noticia."
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
            "generationConfig": {
                "temperature": 0.7,
                "response_mime_type": "application/json"
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            data = response.json()
            
            if "candidates" in data:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
            else:
                print(f"Error Gemini API: {data}")
                return {}
        except Exception as e:
            print(f"Error: {e}")
            return {}

if __name__ == "__main__":
    ai = ContentAI()
    # Prueba pequeña
    print(ai.generate_post_content("Noticia: Apple Vision Pro 2", "news"))
