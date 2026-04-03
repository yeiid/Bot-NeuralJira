import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("NO API KEY FOUND")
    exit(1)

print(f"API Key starts with: {api_key[:10]}...")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
print(f"Requesting URL...")

try:
    resp = requests.get(url, timeout=10)
    print(f"Status Code: {resp.status_code}")
    data = resp.json()
    if 'error' in data:
        print("API Error:", data['error'])
    elif 'models' in data:
        print("------- MODELOS DISPONIBLES QUE SOPORTAN generateContent -------")
        for m in data['models']:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(m['name'])
    else:
        print("Unknown response:", data)
except Exception as e:
    print(f"Request Failed: {e}")
