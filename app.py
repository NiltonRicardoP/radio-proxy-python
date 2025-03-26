from flask import Flask, Response
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import socket
import os
import requests

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
    
@app.route("/currentsong")
def get_current_song():
    try:
        url = "http://82.145.41.50:7005/7.html"
        headers = {
            "User-Agent": "RadioProxy"
        }
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            return {"current_song": "Erro ao acessar rádio"}, 500

        text = response.text
        print("🔍 Conteúdo bruto:", text)

        # Tenta achar algo como "Survivor - Burning Heart"
        match = re.search(r",([^,]+)\s*-\s*([^,]+)\s*\((Video)?\)", text)
        if match:
            artist = match.group(1).strip()
            title = match.group(2).strip()
            return {"current_song": f"{artist} - {title}"}, 200

        # Alternativa baseada no exemplo do 7.html
        parts = text.split(',')
        if len(parts) >= 7:
            return {"current_song": parts[6].strip()}, 200

        return {"current_song": "Dados insuficientes"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

    except Exception as e:
        print("❌ Erro ao acessar rádio:", e)
        return {"error": str(e)}, 500



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
