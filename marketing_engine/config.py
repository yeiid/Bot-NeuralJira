import os
from dataclasses import dataclass
from typing import Dict, Tuple
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

@dataclass
class FacebookConfig:
    page_id: str = os.getenv("FACEBOOK_PAGE_ID", "112603561747066")
    api_version: str = "v19.0"
    access_token: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")

@dataclass
class ImageConfig:
    default_size: Tuple[int, int] = (1080, 1080)
    dpi: int = 300
    format: str = "JPEG"
    quality: int = 95

@dataclass
class ColorPalette:
    primary: str = "#8B5CF6"
    secondary: str = "#3B82F6"
    accent: str = "#10B981"
    warning: str = "#F59E0B"
    danger: str = "#EF4444"
    background: str = "#0F172A"
    surface: str = "#1E293B"
    text_primary: str = "#F8FAFC"
    text_secondary: str = "#CBD5E1"

class Paths:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    
    @classmethod
    def ensure_directories(cls):
        for dir_path in [cls.TEMPLATES_DIR, cls.ASSETS_DIR, cls.FONTS_DIR, cls.OUTPUT_DIR]:
            os.makedirs(dir_path, exist_ok=True)
