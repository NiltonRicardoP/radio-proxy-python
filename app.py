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
    try:
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((RADIO_HOST, RADIO_PORT))

        request = "GET /7.html HTTP/1.0\r\nUser-Agent: RadioProxy\r\n\r\n"
        s.sendall(request.encode())

        response = b""
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            response += chunk

        s.close()

        # Substitui ICY por HTTP para compatibilidade
        if response.startswith(b'ICY'):
            response = response.replace(b'ICY', b'HTTP/1.1', 1)

        # Decodifica a resposta
        decoded = response.decode('utf-8', errors='ignore')

        # Procura a linha com dados da música (última com vírgulas)
        for line in decoded.splitlines()[::-1]:
            if ',' in line:
                parts = line.strip().split(',')
                if len(parts) >= 7:
                    return {"current_song": parts[6].strip()}, 200
                break

        return {"current_song": "Dados insuficientes"}, 200

    except Exception as e:
        print("❌ Erro ao acessar rádio:", e)
        return {"error": str(e)}, 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
