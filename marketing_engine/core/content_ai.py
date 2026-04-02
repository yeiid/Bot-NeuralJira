import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Dict, Any

# Cargar variables de entorno
load_dotenv()

class ContentAI:
    """
    Cerebro del Bot NeuralJira (Claude/Anthropic).
    Toma una noticia o tema y lo convierte en el script para una infografía.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
        self.model = "claude-3-5-sonnet-20240620" # Modelo recomendado para redacción estructurada
    
    def generate_post_content(self, raw_input: str, template_type: str = "tutorial") -> Dict[str, Any]:
        """
        Genera el contenido estructurado (JSON) para un template específico.
        """
        
        system_prompt = f"""
        Eres Galldroko, el estratega de marketing de NeuralJira. 
        Tu misión es tomar una noticia tecnológica o un tutorial técnico y convertirlo en una infografía visual IMPACTANTE.
        
         NeuralJira es una marca de tecnología avanzada con una estética Cyberpunk, Neón, Cyan y Morado. 
         El tono debe ser profesional, directo y orientado a desarrolladores o entusiastas tech.
        
         Debes responder únicamente con un objeto JSON válido que coincida con el esquema del template: {template_type}.
        """
        
        prompt_templates = {
            "tutorial": f"""
                Toma la siguiente información: "{raw_input}"
                Genera un tutorial de 4 pasos claros y concisos. 
                Esquema JSON:
                {{
                    "title": "Un título corto y directo (max 40 caps)",
                    "steps": ["Paso 1: Desc...", "Paso 2: Con...", "Paso 3: Eje...", "Paso 4: Fin..."],
                    "cta": "¡Guarda este post y empieza hoy! 🚀"
                }}
            """,
            "news": f"""
                Toma la siguiente noticia: "{raw_input}"
                Genera un resumen para Facebook.
                Esquema JSON:
                {{
                    "headline": "Titular impactante en español",
                    "body": "Resumen de 3-4 párrafos cortos sobre por qué esto importa.",
                    "source": "NeuralJira News"
                }}
            """,
            "quote": f"""
                Toma este texto: "{raw_input}"
                Encapsúlalo en una cita poderosa.
                Esquema JSON:
                {{
                    "quote": "Cita redactada profesionalmente",
                    "author": "Nombre del autor o 'NeuralJira Insight'"
                }}
            """
        }
        
        user_prompt = prompt_templates.get(template_type, prompt_templates["tutorial"])
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extraer JSON de la respuesta (Claude suele ponerlo entre ```json ... ```)
        content = response.content[0].text
        try:
            # Intentar encontrar el bloque JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content:
                content = content[content.find("{"):content.rfind("}")+1]
            
            return json.loads(content)
        except Exception as e:
            print(f"Error al parsear respuesta de IA: {e}")
            print(f"Respuesta cruda: {content}")
            return {}

if __name__ == "__main__":
    ai = ContentAI()
    # Prueba rápida
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Falta ANTHROPIC_API_KEY en .env")
    else:
        test_news = "Nvidia lanza nuevo chip Blackwell para IA con 208 mil millones de transistores."
        result = ai.generate_post_content(test_news, template_type="news")
        print(json.dumps(result, indent=2, ensure_ascii=False))
