import os
from flask import Flask, Response
import requests
import re

app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 IPTV Server OK - /lista.m3u"

@app.route('/lista.m3u')
def lista():
    return """#EXTM3U
#EXTINF:-1,TEST CHANNEL
http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
