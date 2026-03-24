import requests
import re
import os
from flask import Flask, Response

app = Flask(__name__)

# =====================================================
# 🔧 CONFIGURACIÓN - CAMBIA AQUÍ TUS URLs REALES
# =====================================================
CANALES_CONFIG = [
    {
        "nombre": "ESPN 1", 
        "url_web": "https://la14hd.com/vivo/canales.php?stream=espn",  # ← CAMBIA ESTA URL
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Espn_logo.png/640px-Espn_logo.png"
    },
    {
        "nombre": "FOX SPORTS", 
        "url_web": "https://la14hd.com/vivo/canales.php?stream=foxsports",  # ← CAMBIA ESTA URL
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Fox_Sports_logo.svg/640px-Fox_Sports_logo.svg.png"
    },
    {
        "nombre": "DSPORTS", 
        "url_web": "https://la14hd.com/vivo/canales.php?stream=dsports",  # ← CAMBIA ESTA URL
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/DSports_logo.png/640px-DSports_logo.png"
    }
    # AGREGAR MÁS CANALES: Copia el bloque {} arriba
]

def buscar_token_en_web(url_fuente):
    """Busca y corrige token m3u8 automáticamente"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url_fuente, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Regex mejorada para encontrar m3u8 con token
        patrones = [
            r'https?://[^\s<>"]+\.m3u8\?token=[^\s<>"]+',
            r'https?://[^\s<>"]+\.m3u8[^"\s<>]*(?:token|auth)=[^"\s<>]*',
            r'"([^"]+\.m3u8[^"]*)"',
        ]
        
        for patron in patrones:
            match = re.search(patron, response.text)
            if match:
                url_encontrada = match.group(1) if len(match.groups()) > 0 else match.group(0)
                # ✅ MAGIA: Corrige mono → index
                url_final = url_encontrada.replace("mono.m3u8", "index.m3u8")
                print(f"✅ Token encontrado: {url_final[:100]}...")
                return url_final
        
        print(f"❌ No se encontró token en {url_fuente}")
        return None
        
    except Exception as e:
        print(f"❌ Error en {url_fuente}: {e}")
        return None

@app.route('/lista.m3u')
def generar_lista():
    """Genera lista M3U completa"""
    m3u_content = ["#EXTM3U"]
    canales_funcionando = 0
    
    for canal in CANALES_CONFIG:
        print(f"🔍 Buscando {canal['nombre']}...")
        url_token = buscar_token_en_web(canal["url_web"])
        
        if url_token:
            m3u_content.append(f'#EXTINF:-1 tvg-logo="{canal["logo"]}",{canal["nombre"]}')
            m3u_content.append(url_token)
            canales_funcionando += 1
        else:
            print(f"❌ {canal['nombre']} no disponible")
    
    print(f"✅ Lista generada: {canales_funcionando}/{len(CANALES_CONFIG)} canales")
    return Response("\n".join(m3u_content), mimetype='text/plain')

@app.route('/')
def home():
    return """
    <h1>🚀 Servidor IPTV Activo</h1>
    <p><a href="/lista.m3u">📺 Descargar lista.m3u</a></p>
    <p>Canales funcionando: Revisando...</p>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("🚀 Servidor iniciado en http://127.0.0.1:{}/lista.m3u".format(port))
    app.run(host='0.0.0.0', port=port, debug=False)