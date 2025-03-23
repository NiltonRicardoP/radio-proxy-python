from flask import Flask, Response, request
from flask_cors import CORS
from urllib.parse import urljoin
import urllib3
import os

app = Flask(__name__)
CORS(app)

RADIO_HOST = 'http://82.145.41.50:7005/'

http = urllib3.PoolManager()

@app.route('/')
def index():
    return '🎧 Proxy de rádio online está ativo!'

@app.route('/stream/<path:path>')
def stream(path):
    proxied_url = urljoin(RADIO_HOST, path)
    headers = {
        'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0'),
        'Icy-MetaData': '1',
    }

    try:
        r = http.request('GET', proxied_url, headers=headers, preload_content=False, timeout=10)
        return Response(r.stream(), content_type=r.headers.get('Content-Type', 'audio/mpeg'))
    except Exception as e:
        print(f"Erro ao acessar rádio: {e}")
        return f"Erro ao acessar rádio: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
