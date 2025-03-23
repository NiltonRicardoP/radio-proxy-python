from flask import Flask, Response, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import socket

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

RADIO_HOST = '82.145.41.50'
RADIO_PORT = 7005

@app.route('/')
def index():
    return '🎧 Proxy de rádio online com suporte a ICY está ativo!'

@app.route('/stream')
def stream():
    try:
        # Conexão bruta com socket para lidar com ICY
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((RADIO_HOST, RADIO_PORT))
        sock.sendall(b"GET /;stream.mp3 HTTP/1.0\r\nUser-Agent: VLC/3.0.0\r\n\r\n")

        def generate():
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                yield data

        return Response(generate(), mimetype="audio/mpeg")

    except Exception as e:
        return f"Erro ao acessar rádio: {e}", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)