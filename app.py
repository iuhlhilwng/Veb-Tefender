import requests
import re
import os
import time
import urllib.parse
from flask import Flask, Response, request

app = Flask(__name__)

# 🔥 TUS CANALES - CAMBIA SOLO ESTAS 3 URLs
CANALES_CONFIG = [
    {
        "nombre": "ESPN", 
        "url_web": "https://tu-pagina-real.com/espn", # ← URL #1
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Espn_logo.png/640px-Espn_logo.png"
    },
    {
        "nombre": "FOX SPORTS", 
        "url_web": "https://tu-pagina-real.com/foxsports", # ← URL #2
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Fox_Sports_logo.svg/640px-Fox_Sports_logo.svg.png"
    },
    {
        "nombre": "DSports", 
        "url_web": "https://tu-pagina-real.com/dsports", # ← URL #3
        "logo": "https://via.placeholder.com/300x150/FF0000/FFFFFF?text=DSports"
    }
]

def buscar_token_en_web(url_fuente, max_intentos=3):
    """🔍 Buscador tokens avanzado"""
    headers_lista = [
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    ]
    
    for intento in range(max_intentos):
        for headers in headers_lista:
            try:
                time.sleep(1 + intento)
                response = requests.get(url_fuente, headers=headers, timeout=20)
                
                patrones = [
                    r'https?://[^\s<>"]+\.m3u8(?:\?[^<>" ]*)?',
                    r'"([^"]+\.m3u8[^"]*)"',
                    r'\'([^\']+\.m3u8[^\']*)\''
                ]
                
                for patron in patrones:
                    matches = re.findall(patron, response.text, re.IGNORECASE)
                    for match in matches:
                        url_raw = match if isinstance(match, str) else match[0]
                        url_final = url_raw.replace("mono.m3u8", "index.m3u8")
                        if '.m3u8' in url_final:
                            print(f"✅ TOKEN: {url_final[:80]}")
                            return url_final
            except:
                continue
    return None

@app.route('/')
def home():
    return """
    <h1>🚀 IPTV Server Listo</h1>
    <p><a href="/lista.m3u">📺 Lista M3U</a></p>
    """

@app.route('/lista.m3u')
def generar_lista_m3u():
    """🎥 Lista M3U con proxy anti-bloqueo"""
    m3u_content = ["#EXTM3U"]
    
    for canal in CANALES_CONFIG:
        url_token = buscar_token_en_web(canal["url_web"])
        if url_token:
            # ✅ PROXY ANTI-IP BLOQUEO
            proxy_url = f'/proxy/{urllib.parse.quote_plus(url_token)}'
            m3u_content.append(f'#EXTINF:-1 tvg-logo="{canal["logo"]}",{canal["nombre"]}')
            m3u_content.append(proxy_url)
    
    return Response("\n".join(m3u_content), mimetype='text/plain')

@app.route('/proxy/<path:url_encoded>')
def proxy_stream(url_encoded):
    """🌐 Proxy streams - bypass IP/WiFi bloqueo"""
    try:
        url_real = urllib.parse.unquote(url_encoded)
        headers = {
            'User-Agent': 'VLC/3.0.20 LibVLC/3.0.20',
            'Referer': 'https://www.google.com/',
            'Origin': 'https://www.google.com',
            'X-Forwarded-For': '203.0.113.1', # IP neutra
            'Client-IP': '203.0.113.1'
        }
        
        resp = requests.get(url_real, headers=headers, stream=True, timeout=15)
        resp.raise_for_status()
        
        return Response(
            resp.iter_content(chunk_size=8192),
            content_type=resp.headers.get('Content-Type', 'video/mp2t'),
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'no-cache',
                'Access-Control-Allow-Headers': '*'
            }
        )
    except Exception as e:
        print(f"❌ Proxy error: {e}")
        return "Stream no disponible", 503

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
