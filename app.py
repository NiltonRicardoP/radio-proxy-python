from flask import Flask, Response
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import socket
import os

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

RADIO_HOST = '82.145.41.50'
RADIO_PORT = 7005
RADIO_PATH = '/;stream.mp3'

@app.route('/')
def index():
    return '🎧 Proxy de rádio Shoutcast com correção de cabeçalho está ativo!'

@app.route('/stream')
def stream():
    try:
        print("🔁 Conectando ao servidor Shoutcast...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((RADIO_HOST, RADIO_PORT))
        s.sendall(f"GET {RADIO_PATH} HTTP/1.0\r\nUser-Agent: RadioProxy\r\n\r\n".encode())

        # Lê o cabeçalho
        buffer = b""
        while b"\r\n\r\n" not in buffer:
            buffer += s.recv(1)

        header, rest = buffer.split(b"\r\n\r\n", 1)

        # Corrige o cabeçalho ICY para HTTP/1.1
        if header.startswith(b"ICY"):
            header = header.replace(b"ICY", b"HTTP/1.1", 1)

        def generate():
            yield header + b"\r\n\r\n" + rest
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                yield chunk

        print("✅ Streaming iniciado")
        return Response(generate(), content_type="audio/mpeg")

    except Exception as e:
        print("❌ Erro ao acessar rádio:", e)
        return f"Erro ao acessar rádio: {e}", 500
    
@app.route('/currentsong')
def currentsong():
    import socket
    try:
        host = '82.145.41.50'
        port = 7005
        path = '/7.html'

        # Conectar ao servidor
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        s.sendall(f"GET {path} HTTP/1.0\r\nUser-Agent: RadioProxy\r\n\r\n".encode())

        # Recebe resposta
        response = b""
        while True:
            data = s.recv(1024)
            if not data:
                break
            response += data
        s.close()

        # Ajusta o cabeçalho ICY para HTTP padrão (se necessário)
        response = response.replace(b'ICY 200 OK', b'HTTP/1.1 200 OK')

        # Separa cabeçalhos e corpo da resposta
        headers, body = response.split(b'\r\n\r\n', 1)

        # Decodifica o corpo para texto e extrai a música atual
        body_text = body.decode('utf-8', errors='ignore')

        # Extrai música atual da resposta original
        current_song = body_text.split(',')[6].split('</body>')[0]

        return {"current_song": current_song}, 200
    except Exception as e:
        print("Erro ao acessar rádio:", e)
        return {"error": f"Erro: {e}"}, 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
