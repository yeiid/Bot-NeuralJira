# Bot NeuralJira (Marketing Engine)

Este repositorio contiene los scripts de automatización de marketing y publicación de Facebook para la marca **NeuralJira**, operados de manera autónoma por el Agente IA **Galldroko** a través de la infraestructura **OpenClaw**.

## Arquitectura del Agente (OpenClaw)

1. **Integración Actual:** OpenClaw corre como un servicio silencioso (Daemon/Gateway) en un entorno de pruebas Linux (VPS Sandbox). Está enganchado a Telegram para recibir comandos, pero opera asíncronamente mediante `HEARTBEAT.md` y tareas programadas (*Cron-jobs*).
2. **LLMs Conectados (Cerebro del Agente):**
   - **Primario:** `google/gemini-3.1-pro-preview` (200k Contexto).
   - **Pool de Respaldo (En TOOLS.md):** Groq (Llama 3.1 8B/70B), Cerebras, DeepSeek, SambaNova y OpenRouter (Acceso a Claude y GPT).
3. **Flujo de Automatización:**
   - Cero intervención humana. El agente ejecuta directamente los scripts de Python en la carpeta `marketing_engine/`.
   - Se alimenta de llamadas a APIs REST (Groq para redacción, Facebook Graph API para publicación).

## Generación de Imágenes (Estrategia Híbrida)

El Agente Galldroko puede generar imágenes de dos maneras:

### 1. Herramienta Nativa (IA Generativa)
OpenClaw tiene integrada la *tool* nativa `image_generate` (basada en el modelo `google/gemini-3.1-flash-image-preview` o equivalente).
- **Uso:** El agente invoca `call:default_api:image_generate{prompt: "Cyberpunk neon..."}` y recibe un archivo multimedia.
- **Problema en B2B:** La IA no escribe texto perfecto (errores de ortografía en inglés/español). Para infografías y paso-a-paso, se ve poco profesional.

### 2. Motor de Renderizado 2D (Python Pillow) - [Activo]
Para resolver el problema de la IA, usamos el script `gen_infographic.py` incluido en este repositorio.
- **Cómo funciona:** Usa la librería `Pillow` de Python para dibujar cajas modulares, colores hexadecimales exactos de la marca (Neón, Cyan, Morado) y la tipografía `FiraCode.ttf`.
- **Ventaja:** El texto extraído por los LLMs se inyecta en el script de Python, garantizando ortografía humana y limpieza visual.

## Archivos de Configuración OpenClaw
El agente lee su comportamiento de archivos inyectados en su *Workspace* (`/root/.openclaw/workspace/`):
- `SOUL.md`: Personalidad estricta y directa de Galldroko.
- `USER.md`: Ficha técnica de Yeiid (Horarios, Proyectos).
- `HEARTBEAT.md`: Reglas de ejecución por intervalos de tiempo.
- `TOOLS.md`: Claves de API cifradas.
