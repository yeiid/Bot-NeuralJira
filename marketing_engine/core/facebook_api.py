import requests
import json
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from config import FacebookConfig

@dataclass
class FacebookPost:
    message: str
    image_path: str
    page_id: Optional[str] = None
    published: bool = True

class FacebookAPI:
    def __init__(self, config: Optional[FacebookConfig] = None):
        self.config = config or FacebookConfig()
        self.base_url = f"https://graph.facebook.com/{self.config.api_version}"
    
    def upload_photo(self, post: FacebookPost) -> Tuple[bool, Dict]:
        """
        Sube foto a Facebook con manejo de errores profesional
        """
        try:
            # Validar que la imagen existe
            if not os.path.exists(post.image_path):
                return False, {"error": "Image file not found"}
            
            # Preparar datos para la API
            url = f"{self.base_url}/{post.page_id or self.config.page_id}/photos"
            
            data = {
                'message': post.message,
                'published': str(post.published).lower(),
                'access_token': self.config.access_token
            }
            
            # Adjuntar imagen
            with open(post.image_path, 'rb') as image_file:
                files = {'source': image_file}
                
                response = requests.post(url, data=data, files=files, timeout=30)
            
            # Procesar respuesta
            if response.status_code == 200:
                result = response.json()
                return True, {
                    "post_id": result.get('id'),
                    "url": result.get('post_id'),
                    "success": True
                }
            else:
                error_data = response.json() if response.content else {}
                return False, {
                    "error": error_data.get('error', {}).get('message', f'HTTP {response.status_code}'),
                    "code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Network error: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}
    
    def create_post_with_image(self, message: str, image_path: str, 
                             published: bool = True) -> Tuple[bool, Dict]:
        """
        Método simplificado para crear post con imagen
        """
        post = FacebookPost(
            message=message,
            image_path=image_path,
            published=published
        )
        
        return self.upload_photo(post)
    
    def validate_connection(self) -> Tuple[bool, str]:
        """
        Valida la conexión con la API de Facebook
        """
        try:
            url = f"{self.base_url}/me"
            params = {'access_token': self.config.access_token}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                return True, f"Connected as: {user_data.get('name', 'Unknown')}"
            else:
                error_data = response.json() if response.content else {}
                return False, error_data.get('error', {}).get('message', 'Connection failed')
                
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def get_page_info(self) -> Tuple[bool, Dict]:
        """
        Obtiene información de la página
        """
        try:
            url = f"{self.base_url}/{self.config.page_id}"
            params = {
                'access_token': self.config.access_token,
                'fields': 'name,fan_count,link'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": "Failed to get page info"}
                
        except Exception as e:
            return False, {"error": str(e)}

class PostScheduler:
    """
    Clase para programar posts (futura implementación)
    """
    def __init__(self, facebook_api: FacebookAPI):
        self.facebook_api = facebook_api
    
    def schedule_post(self, post: FacebookPost, scheduled_time: str) -> Tuple[bool, Dict]:
        """
        Programa un post para publicación futura
        """
        # Implementación futura con base de datos local
        pass
    
    def get_scheduled_posts(self) -> list:
        """
        Obtiene lista de posts programados
        """
        # Implementación futura
        pass
