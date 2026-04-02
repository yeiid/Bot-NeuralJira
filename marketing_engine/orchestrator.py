import os
import sys
import json
import logging
from typing import Dict, Any

# Añadir el directorio actual al path para importaciones limpias
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.news_fetcher import NewsFetcher
from core.content_ai import ContentAI
from gen_infographic import generate as generate_image
from core.facebook_api import FacebookAPI

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("marketing_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")

class MarketingOrchestrator:
    """
    El 'Sistema Nervioso' de NeuralJira. 
    Coordina la búsqueda, redacción, diseño y publicación.
    """
    
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.content_ai = ContentAI()
        self.facebook_api = FacebookAPI()
        logger.info("Orchestrator inicializado correctamente.")

    def run_news_cycle(self, source: str = None) -> Dict[str, Any]:
        """
        Ciclo Completo: Noticia -> IA -> Imagen -> Facebook
        """
        try:
            # 1. Obtener noticia
            logger.info(f"Buscando noticias... (Fuente: {source or 'Aleatoria'})")
            news_item = self.news_fetcher.get_random_news_item()
            if not news_item:
                return {"success": False, "error": "No se encontraron noticias."}
            
            logger.info(f"Noticia encontrada: {news_item['title']}")
            
            # 2. Redactar contenido con IA
            logger.info("Redactando post con Claude AI...")
            input_text = f"Título: {news_item['title']}\nResumen: {news_item['summary']}"
            post_data = self.content_ai.generate_post_content(input_text, template_type="news")
            
            if not post_data:
                return {"success": False, "error": "Error al generar contenido con IA."}
            
            # 3. Generar Imagen
            logger.info("Generando infografía profesional...")
            image_path = generate_image("news", post_data)
            logger.info(f"Imagen generada en: {image_path}")
            
            # 4. Publicar en Facebook
            logger.info("Subiendo a Facebook...")
            fb_message = f"🚀 {post_data['headline']}\n\n{post_data['body']}\n\n#NeuralJira #TechNews #AI #Cyberpunk"
            
            success, fb_result = self.facebook_api.create_post_with_image(fb_message, image_path)
            
            if success:
                logger.info(f"¡ÉXITO! Post publicado. ID: {fb_result.get('post_id')}")
                return {"success": True, "post_id": fb_result.get('post_id'), "image": image_path}
            else:
                logger.error(f"Error en Facebook: {fb_result.get('error')}")
                return {"success": False, "error": fb_result.get('error')}

        except Exception as e:
            logger.exception("Fallo catastrófico en el ciclo de noticias.")
            return {"success": False, "error": str(e)}

    def run_tutorial_cycle(self, topic: str) -> Dict[str, Any]:
        """
        Ciclo de Tutorial: Tema -> IA -> Imagen -> Facebook
        """
        # Similar al de noticias pero forzando template 'tutorial'
        try:
            logger.info(f"Creando tutorial sobre: {topic}")
            post_data = self.content_ai.generate_post_content(topic, template_type="tutorial")
            
            if not post_data:
                return {"success": False, "error": "IA no pudo generar el tutorial."}
                
            image_path = generate_image("tutorial", post_data)
            
            fb_message = f"🛠️ GUÍA RÁPIDA: {post_data['title']}\n\nDesliza para ver los pasos. ¡Guarda esta infografía! 💾\n\n#NeuralJira #Tutorial #DevLife #Hacking"
            
            success, fb_result = self.facebook_api.create_post_with_image(fb_message, image_path)
            return {"success": success, "result": fb_result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    orchestrator = MarketingOrchestrator()
    # Ejecución manual de prueba
    if len(sys.argv) > 1 and sys.argv[1] == "--news":
        print(json.dumps(orchestrator.run_news_cycle(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--tutorial":
        topic = sys.argv[2] if len(sys.argv) > 2 else "Python para principiantes"
        print(json.dumps(orchestrator.run_tutorial_cycle(topic), indent=2))
    else:
        print("Uso: python orchestrator.py [--news | --tutorial 'tema']")
