from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from config import ImageConfig, ColorPalette, Paths

@dataclass
class TextElement:
    text: str
    position: Tuple[int, int]
    font_size: int
    color: str
    font_style: str = "normal"
    max_width: Optional[int] = None

@dataclass
class ShapeElement:
    shape_type: str  # "rectangle", "circle", "line"
    coordinates: List[Tuple[int, int]]
    fill_color: Optional[str] = None
    outline_color: Optional[str] = None
    width: int = 1

class ProfessionalImageGenerator:
    def __init__(self):
        self.config = ImageConfig()
        self.colors = ColorPalette()
        Paths.ensure_directories()
        self._load_fonts()
    
    def _load_fonts(self):
        """Carga fuentes profesionales con fallbacks"""
        try:
            # Intentar cargar fuentes profesionales
            self.fonts = {
                "bold": self._get_font("Inter-Bold.ttf", 60),
                "regular": self._get_font("Inter-Regular.ttf", 40),
                "light": self._get_font("Inter-Light.ttf", 30),
                "title": self._get_font("Montserrat-Bold.ttf", 80)
            }
        except:
            # Fallback a fuentes del sistema
            self.fonts = {
                "bold": ImageFont.load_default(),
                "regular": ImageFont.load_default(),
                "light": ImageFont.load_default(),
                "title": ImageFont.load_default()
            }
    
    def _get_font(self, font_name: str, size: int) -> ImageFont.ImageFont:
        """Intenta cargar fuente desde assets o sistema"""
        font_path = os.path.join(Paths.FONTS_DIR, font_name)
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        
        # Fallback a fuentes del sistema
        system_fonts = [
            "arial.ttf", "arialbd.ttf", "ariali.ttf",
            "calibri.ttf", "calibrib.ttf", "verdana.ttf"
        ]
        
        for sys_font in system_fonts:
            try:
                return ImageFont.truetype(sys_font, size)
            except:
                continue
        
        return ImageFont.load_default()
    
    def create_from_template(self, template_path: str, data: Dict) -> Image.Image:
        """Crea imagen desde template JSON"""
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
        
        # Crear imagen base
        img = Image.new('RGB', 
                        tuple(template.get('size', self.config.default_size)), 
                        template.get('background', self.colors.background))
        
        draw = ImageDraw.Draw(img)
        
        # Dibujar elementos del template
        if 'shapes' in template:
            for shape_data in template['shapes']:
                self._draw_shape(draw, shape_data)
        
        if 'text_elements' in template:
            for text_data in template['text_elements']:
                self._draw_text(draw, text_data, data)
        
        # Aplicar efectos profesionales
        if template.get('effects', {}).get('shadow', False):
            img = self._apply_shadow(img)
        
        if template.get('effects', {}).get('gradient', False):
            img = self._apply_gradient(img, template['effects'].get('gradient_colors', []))
        
        return img
    
    def _draw_shape(self, draw: ImageDraw.ImageDraw, shape_data: Dict):
        """Dibuja formas geométricas"""
        shape = ShapeElement(**shape_data)
        
        if shape.shape_type == "rectangle":
            draw.rectangle(shape.coordinates, 
                          fill=shape.fill_color, 
                          outline=shape.outline_color, 
                          width=shape.width)
        elif shape.shape_type == "circle":
            draw.ellipse(shape.coordinates, 
                        fill=shape.fill_color, 
                        outline=shape.outline_color, 
                        width=shape.width)
        elif shape.shape_type == "line":
            draw.line(shape.coordinates, 
                     fill=shape.outline_color, 
                     width=shape.width)
    
    def _draw_text(self, draw: ImageDraw.ImageDraw, text_data: Dict, variables: Dict):
        """Dibuja texto con soporte para variables"""
        # Reemplazar variables en el texto
        text = text_data['text']
        for key, value in variables.items():
            text = text.replace(f"{{{key}}}", str(value))
        
        element = TextElement(
            text=text,
            position=tuple(text_data['position']),
            font_size=text_data.get('font_size', 40),
            color=text_data.get('color', self.colors.text_primary),
            font_style=text_data.get('font_style', 'regular'),
            max_width=text_data.get('max_width')
        )
        
        font = self.fonts.get(element.font_style, self.fonts['regular'])
        
        if element.max_width:
            # Texto con ajuste de línea
            lines = self._wrap_text(element.text, font, element.max_width)
            y_offset = 0
            for line in lines:
                draw.text((element.position[0], element.position[1] + y_offset), 
                         line, fill=element.color, font=font)
                y_offset += font.size + 5
        else:
            draw.text(element.position, element.text, fill=element.color, font=font)
    
    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        """Ajusta texto a múltiples líneas"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.getlength(test_line) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _apply_shadow(self, img: Image.Image) -> Image.Image:
        """Aplica efecto de sombra profesional"""
        shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # Crear sombra sutil
        shadow_draw.rectangle([10, 10, img.size[0]-10, img.size[1]-10], 
                            fill=(0, 0, 0, 50))
        
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5))
        
        # Combinar imagen original con sombra
        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(shadow, (0, 0))
        result.paste(img, (0, 0))
        
        return result.convert('RGB')
    
    def _apply_gradient(self, img: Image.Image, colors: List[str]) -> Image.Image:
        """Aplica gradiente de fondo"""
        if not colors:
            return img
        
        width, height = img.size
        gradient = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(gradient)
        
        # Crear gradiente vertical
        for i in range(height):
            ratio = i / height
            r = int(self._hex_to_rgb(colors[0])[0] * (1 - ratio) + self._hex_to_rgb(colors[1])[0] * ratio)
            g = int(self._hex_to_rgb(colors[0])[1] * (1 - ratio) + self._hex_to_rgb(colors[1])[1] * ratio)
            b = int(self._hex_to_rgb(colors[0])[2] * (1 - ratio) + self._hex_to_rgb(colors[1])[2] * ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Combinar con imagen original
        img = Image.alpha_composite(gradient.convert("RGBA"), img.convert("RGBA"))
        return img.convert("RGB")
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convierte color hex a RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def save_image(self, img: Image.Image, filename: str) -> str:
        """Guarda imagen con alta calidad"""
        if not filename.endswith(('.jpg', '.jpeg', '.png')):
            filename += '.jpg'
        
        output_path = os.path.join(Paths.OUTPUT_DIR, filename)
        img.save(output_path, 
                format=self.config.format, 
                quality=self.config.quality,
                dpi=(self.config.dpi, self.config.dpi))
        
        return output_path
