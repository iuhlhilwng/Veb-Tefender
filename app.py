import requests
import re
import os
from flask import Flask, Response

app = Flask(__name__)

# 🔥 TUS CANALES REALES - CAMBIA SOLO ESTAS URLs
CANALES_CONFIG = [
    {
        "nombre": "ESPN", 
        "url_web": "https://tu-pagina-real.com/espn", # ← PON TU URL AQUÍ
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Espn_logo.png/640px-Espn_logo.png"
    },
    {
        "nombre": "FOX SPORTS", 
        "url_web": "https://tu-pagina-real.com/foxsports", # ← PON TU URL AQUÍ
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Fox_Sports_logo.svg/640px-Fox_Sports_logo.svg.png"
    },
    {
        "nombre": "DSports", 
        "url_web": "https://tu-pagina-real.com/dsports", # ← PON TU URL AQUÍ
        "logo": "https://i.imgur.com/DSportsLogo.png"
    }
    # AGREGAR MÁS: copia bloque arriba
]

def buscar_token_en_web(url_fuente):
    """🔍 Busca m3u8 + token Y corrige mono→index"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url_fuente, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 🔎 Regex MÚLTIPLES patrones
        patrones = [
            r'https?://[^\s<>"]+\.m3u8\?token=[^\s<>"]+',
            r'https?://[^\s<>"]+\.m3u8[^<>"]*token[^<>"]*',
            r'"(https?://[^\s<>"]+\.m3u8[^"]*)"'
        ]
        
        for patron in patrones:
            match = re.search(patron, response.text, re.IGNORECASE)
            if match:
                url_raw = match.group(1) if match.groups() else match.group(0)
                # ✨ MAGIA: mono.m3u8 → index.m3u8
                url_final = url_raw.replace("mono.m3u8", "index.m3u8")
                print(f"✅ {url_fuente} → {url_final[:80]}...")
                return url_final
        
        print(f"❌ No token en {url_fuente}")
        return None
        
    except Exception as e:
        print(f"❌ Error {url_fuente}: {e}")
        return None

@app.route('/')
def home():
    return """
    <h1>🚀 IPTV Server Activo</h1>
    <a href="/lista.m3u">📺 Lista M3U</a>
    """

@app.route('/lista.m3u')
def generar_lista_m3u():
    """🎥 Genera lista IPTV dinámica"""
    m3u_content = ["#EXTM3U"]
    total_canales = len(CANALES_CONFIG)
    canales_ok = 0
    
    for canal in CANALES_CONFIG:
        print(f"🔍 Buscando {canal['nombre']}...")
        url_token = buscar_token_en_web(canal["url_web"])
        
        if url_token:
            m3u_content.append(f'#EXTINF:-1 tvg-logo="{canal["logo"]}",{canal["nombre"]}')
            m3u_content.append(url_token)
            canales_ok += 1
            print(f"✅ {canal['nombre']} OK")
        else:
            print(f"❌ {canal['nombre']} falló")
    
    print(f"📊 Lista: {canales_ok}/{total_canales} canales")
    return Response("\n".join(m3u_content), mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("🚀 Server iniciado!")
    app.run(host='0.0.0.0', port=port)
