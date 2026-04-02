#!/usr/bin/env python3
"""
NeuralJira Marketing Engine - Generador Profesional de Posts para Facebook
Sistema avanzado para crear imágenes profesionales y publicar en Facebook
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

# Importar módulos del sistema
from core.image_generator import ProfessionalImageGenerator
from core.facebook_api import FacebookAPI, FacebookPost
from config import Paths, FacebookConfig

class MarketingEngine:
    def __init__(self):
        self.image_generator = ProfessionalImageGenerator()
        self.facebook_api = FacebookAPI()
        
    def create_tutorial_post(self, data: Dict) -> str:
        """
        Crea un post tipo tutorial con pasos numerados
        """
        template_path = os.path.join(Paths.TEMPLATES_DIR, "tutorial.json")
        
        # Datos por defecto si no se proporcionan
        default_data = {
            "brand_name": "NEURALJIRA",
            "title": "TÍTULO DEL TUTORIAL",
            "step1_title": "PASO 1:",
            "step1_description": "Descripción del primer paso",
            "step2_title": "PASO 2:",
            "step2_description": "Descripción del segundo paso",
            "step3_title": "PASO 3:",
            "step3_description": "Descripción del tercer paso",
            "step4_title": "PASO 4:",
            "step4_description": "Descripción del cuarto paso",
            "call_to_action": "¡Guarda este post y empieza hoy! 🚀"
        }
        
        # Combinar datos proporcionados con defaults
        post_data = {**default_data, **data}
        
        # Generar imagen
        img = self.image_generator.create_from_template(template_path, post_data)
        
        # Guardar con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tutorial_{timestamp}.jpg"
        return self.image_generator.save_image(img, filename)
    
    def create_quote_post(self, data: Dict) -> str:
        """
        Crea un post con cita inspiracional
        """
        template_path = os.path.join(Paths.TEMPLATES_DIR, "quote.json")
        
        default_data = {
            "quote_text": "Tu cita inspiracional aquí",
            "author_name": "- Autor",
            "brand_name": "NEURALJIRA"
        }
        
        post_data = {**default_data, **data}
        
        img = self.image_generator.create_from_template(template_path, post_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quote_{timestamp}.jpg"
        return self.image_generator.save_image(img, filename)
    
    def create_comparison_post(self, data: Dict) -> str:
        """
        Crea un post de comparación VS
        """
        template_path = os.path.join(Paths.TEMPLATES_DIR, "comparison.json")
        
        default_data = {
            "brand_name": "NEURALJIRA",
            "title": "COMPARACIÓN: OPCIÓN 1 VS OPCIÓN 2",
            "option1_title": "OPCIÓN 1",
            "option1_description": "Ventajas y características de la opción 1",
            "option2_title": "OPCIÓN 2", 
            "option2_description": "Ventajas y características de la opción 2"
        }
        
        post_data = {**default_data, **data}
        
        img = self.image_generator.create_from_template(template_path, post_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{timestamp}.jpg"
        return self.image_generator.save_image(img, filename)
    
    def publish_to_facebook(self, image_path: str, message: str) -> tuple:
        """
        Publica imagen en Facebook con manejo de errores
        """
        success, result = self.facebook_api.create_post_with_image(message, image_path)
        
        if success:
            print(f"✅ Post publicado exitosamente!")
            print(f"📎 Post ID: {result.get('post_id')}")
            return True, result
        else:
            print(f"❌ Error al publicar: {result.get('error')}")
            return False, result
    
    def validate_facebook_connection(self) -> bool:
        """
        Valida la conexión con Facebook API
        """
        success, message = self.facebook_api.validate_connection()
        if success:
            print(f"✅ {message}")
            return True
        else:
            print(f"❌ Error de conexión: {message}")
            return False

def main():
    """
    Función principal con ejemplos de uso
    """
    engine = MarketingEngine()
    
    print("🚀 NeuralJira Marketing Engine")
    print("=" * 50)
    
    # Validar conexión con Facebook
    print("📡 Validando conexión con Facebook...")
    if not engine.validate_facebook_connection():
        print("⚠️  No se pudo conectar a Facebook. Las imágenes se generarán pero no se publicarán.")
    
    # Ejemplo 1: Tutorial de Python en Android
    print("\n📱 Creando tutorial: Python en Android...")
    tutorial_data = {
        "brand_name": "NEURALJIRA",
        "title": "CÓMO INSTALAR PYTHON EN ANDROID",
        "step1_title": "PASO 1:",
        "step1_description": "Descarga 'Pydroid 3' en la Play Store",
        "step2_title": "PASO 2:",
        "step2_description": "Abre la app y entra al menú lateral",
        "step3_title": "PASO 3:",
        "step3_description": "Toca 'Pip' para instalar librerías",
        "step4_title": "PASO 4:",
        "step4_description": "Escribe tu primer print('Hola')",
        "call_to_action": "Guarda este post y empieza hoy 🚀"
    }
    
    tutorial_image = engine.create_tutorial_post(tutorial_data)
    print(f"✅ Imagen generada: {tutorial_image}")
    
    # Mensaje para Facebook
    fb_message = """🚀 ¿Crees que necesitas una laptop de $1000 USD para programar? MENTIRA. 

Tu celular Android tiene más poder de cómputo que la nave que llegó a la luna. Así es como instalas un entorno de Python real y funcional en 4 pasos sin gastar un peso.

1️⃣ Instala Pydroid 3
2️⃣ Usa PIP para descargar librerías
3️⃣ Ejecuta código de verdad

Guarda esta infografía porque mañana te enseño cómo hackear metadatos (OSINT) desde la misma app. 👇

#NeuralJira #Python #Programacion #DesarrolloWeb #Android"""
    
    # Publicar en Facebook
    print("\n📤 Publicando en Facebook...")
    success, result = engine.publish_to_facebook(tutorial_image, fb_message)
    
    # Ejemplo 2: Cita motivacional
    print("\n💭 Creando cita motivacional...")
    quote_data = {
        "quote_text": "El código es como el humor. Cuando tienes que explicarlo, es malo.",
        "author_name": "- Cory House",
        "brand_name": "NEURALJIRA"
    }
    
    quote_image = engine.create_quote_post(quote_data)
    print(f"✅ Imagen generada: {quote_image}")
    
    # Ejemplo 3: Comparación
    print("\n⚖️  Creando comparación...")
    comparison_data = {
        "brand_name": "NEURALJIRA",
        "title": "PROGRAMACIÓN: LAPTOP VS CELULAR",
        "option1_title": "LAPTOP $1000",
        "option1_description": "✅ Potente\n✅ Teclado completo\n❌ Costoso\n❌ No portable",
        "option2_title": "CELULAR ANDROID",
        "option2_description": "✅ Gratis si ya lo tienes\n✅ Ultra portable\n✅ Apps de desarrollo\n❌ Pantalla pequeña"
    }
    
    comparison_image = engine.create_comparison_post(comparison_data)
    print(f"✅ Imagen generada: {comparison_image}")
    
    print("\n🎉 Proceso completado!")
    print(f"📁 Todas las imágenes guardadas en: {Paths.OUTPUT_DIR}")

if __name__ == "__main__":
    main()
