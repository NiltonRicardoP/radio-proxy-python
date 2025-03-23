from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import urljoin
import requests
from flask import Response, request
import os

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

RADIO_HOST = 'http://82.145.41.50:7005/'

@app.route('/')
def index():
    return '🎧 Proxy de rádio online está ativo!'

@app.route('/stream/<path:path>')
def stream(path):
    # Repassa tudo para o servidor Shoutcast
    proxied_url = urljoin(RADIO_HOST, path)
    headers = {'User-Agent': request.headers.get('User-Agent', '')}
    try:
        r = requests.get(proxied_url, headers=headers, stream=True, timeout=10)
        return Response(r.iter_content(chunk_size=1024), content_type=r.headers['Content-Type'])
    except Exception as e:
        return f"Erro ao acessar rádio: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)