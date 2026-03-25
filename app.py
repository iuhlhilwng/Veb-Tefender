import requests
import re
import os
import time
from flask import Flask, Response

app = Flask(__name__)

# 🔥 TUS CANALES REALES - CAMBIA AQUÍ TUS URLs
CANALES_CONFIG = [
    {
        "nombre": "ESPN", 
        "url_web": "https://la14hd.com/vivo/canales.php?stream=espn", # ← TU URL #1
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Espn_logo.png/640px-Espn_logo.png"
    },
    {
        "nombre": "FOX SPORTS", 
        "url_web": "https://la14hd.com/vivo/canales.php?stream=foxsports", # ← TU URL #2
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Fox_Sports_logo.svg/640px-Fox_Sports_logo.svg.png"
    },
    {
        "nombre": "DSports", 
        "url_web": "https://la14hd.com/vivo/canales.php?stream=dsports", # ← TU URL #3
        "logo": "https://via.placeholder.com/300x150/FF0000/FFFFFF?text=DSports"
    }
    # ➕ MÁS CANALES: copia bloque arriba
]

def buscar_token_en_web(url_fuente, max_intentos=3):
    """🔍 Anti-JS lazyload + Multi-intentos + Headers rotativos"""
    headers_lista = [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': url_fuente
        },
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,*/*;q=0.9',
            'Referer': 'https://www.google.com/'
        }
    ]
    
    for intento in range(max_intentos):
        print(f"🔄 Intento {intento+1}/{max_intentos} para {url_fuente}")
        
        for headers in headers_lista:
            try:
                # ⏳ Espera carga JS progresiva
                espera = 1 + (intento * 2)
                time.sleep(espera)
                
                response = requests.get(url_fuente, headers=headers, timeout=20)
                response.raise_for_status()
                
                print(f"📄 Status: {response.status_code} | Longitud: {len(response.text)}")
                
                # 🔎 Regex AGRESIVO - todos los patrones posibles
                patrones = [
                    r'https?://[^\s<>"\']+\.m3u8(?:\?[^<>"\']*)?',
                    r'(?:src=|href=|url=)("|\')([^"\']+\.m3u8[^"\']*)["\']',
                    r'm3u8[^<>"\']*(?:token|auth|key)=[^<>"\']*',
                    r'"([^"]+\.m3u8[^"]*)"',
                    r'\'([^\']+\.m3u8[^\' ]*)\''
                ]
                
                for patron in patrones:
                    matches = re.findall(patron, response.text, re.IGNORECASE)
                    for match in matches:
                        url_raw = match[1] if isinstance(match, tuple) else match
                        # ✨ MÁGICA CONVERSIÓN
                        url_final = url_raw.replace("mono.m3u8", "index.m3u8")
                        if '.m3u8' in url_final.lower():
                            print(f"✅ ¡TOKEN ENCONTRADO! {url_final[:100]}...")
                            return url_final
                
            except Exception as e:
                print(f"❌ Error intento {intento+1}: {str(e)[:80]}")
                continue
    
    print(f"💥 FALLÓ COMPLETO: {url_fuente}")
    return None

@app.route('/')
def home():
    return f"""
    <h1>🚀 IPTV Server Activo</h1>
    <p><a href="/lista.m3u">📺 Descargar Lista M3U ({len(CANALES_CONFIG)} canales)</a></p>
    <script>location.href='/lista.m3u';</script>
    """

@app.route('/lista.m3u')
def generar_lista_m3u():
    """🎥 Generador M3U dinámico"""
    m3u_content = ["#EXTM3U"]
    total = len(CANALES_CONFIG)
    ok = 0
    
    for canal in CANALES_CONFIG:
        print(f"\n🔍 Procesando {canal['nombre']}...")
        url_token = buscar_token_en_web(canal["url_web"])
        
        if url_token:
            m3u_content.append(f'#EXTINF:-1 tvg-logo="{canal["logo"]}",{canal["nombre"]}')
            m3u_content.append(url_token)
            ok += 1
            print(f"✅ {canal['nombre']} → OK")
        else:
            print(f"❌ {canal['nombre']} → Sin stream")
    
    print(f"\n📊 RESUMEN: {ok}/{total} canales funcionando")
    return Response("\n".join(m3u_content), mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Server en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
