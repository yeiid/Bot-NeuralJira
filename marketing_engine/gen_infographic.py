from PIL import Image, ImageDraw, ImageFont
import urllib.request, urllib.parse, json, os

# Create image
img = Image.new('RGB', (1080, 1080), color=(15, 23, 42))
d = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype('/usr/share/fonts/opentype/firacode/FiraCode-Bold.ttf', 80)
    font_subtitle = ImageFont.truetype('/usr/share/fonts/opentype/firacode/FiraCode-Bold.ttf', 50)
    font_text = ImageFont.truetype('/usr/share/fonts/opentype/firacode/FiraCode-Regular.ttf', 40)
except:
    font_title = ImageFont.load_default()
    font_subtitle = font_title
    font_text = font_title

# Draw NEURALJIRA Logo
d.text((50, 50), "NEURALJIRA", fill=(192, 132, 252), font=font_title)
d.line([(50, 150), (1030, 150)], fill=(56, 189, 248), width=5)

d.text((50, 200), "CÓMO INSTALAR PYTHON EN ANDROID", fill=(248, 250, 252), font=font_subtitle)

steps = [
    ("PASO 1", "Descarga 'Pydroid 3' en la Play Store.", (56, 189, 248)),
    ("PASO 2", "Abre la app y entra al menú lateral.", (16, 185, 129)),
    ("PASO 3", "Toca 'Pip' para instalar librerías.", (245, 158, 11)),
    ("PASO 4", "Escribe tu primer print('Hola').", (239, 68, 68))
]

y = 350
for step, desc, color in steps:
    d.rectangle([(50, y), (1030, y+120)], fill=(30, 41, 59), outline=color, width=3)
    d.text((70, y+30), step + ":", fill=color, font=font_text)
    d.text((250, y+30), desc, fill=(203, 213, 225), font=font_text)
    y += 160

d.text((50, y+50), "Guarda este post y empieza hoy 🚀", fill=(96, 165, 250), font=font_text)

img.save('infografia.jpg')

# Upload to Facebook
# Using curl via os.system for multipart
text = """🚀 ¿Crees que necesitas una laptop de $1000 USD para programar? MENTIRA. 

Tu celular Android tiene más poder de cómputo que la nave que llegó a la luna. Así es como instalas un entorno de Python real y funcional en 4 pasos sin gastar un peso.

1️⃣ Instala Pydroid 3
2️⃣ Usa PIP para descargar librerías
3️⃣ Ejecuta código de verdad

Guarda esta infografía porque mañana te enseño cómo hackear metadatos (OSINT) desde la misma app. 👇

#NeuralJira #Python #Programacion #DesarrolloWeb #Android"""

token = "os.getenv("FB_ACCESS_TOKEN")"
os.system(f'curl -s -X POST "https://graph.facebook.com/v19.0/112603561747066/photos" -F "message={text}" -F "source=@infografia.jpg" -F "access_token={token}"')
