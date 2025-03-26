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

        # Substitui ICY por HTTP para evitar erro no decode
        if response.startswith(b'ICY'):
            response = response.replace(b'ICY', b'HTTP/1.1', 1)

        # Decodifica com tolerância a erros
        response_text = response.decode('utf-8', errors='ignore')

        # Primeiro tenta localizar <body>...</body>
        if "<body>" in response_text and "</body>" in response_text:
            body = response_text.split("<body>")[1].split("</body>")[0].strip()
        else:
            # Se não tiver <body>, tenta encontrar diretamente a linha com os dados
            lines = response_text.splitlines()
            # Pega a última linha não vazia como fallback
            body = ""
            for line in reversed(lines):
                if line.strip():
                    body = line.strip()
                    break

        parts = body.split(',')
        if len(parts) >= 7:
            current_song = parts[6].strip()
        else:
            current_song = f"Dados insuficientes: {body}"

        return {"current_song": current_song}, 200

    except Exception as e:
        print("❌ Erro ao buscar música atual:", e)
        return {"error": str(e)}, 500

    
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

        # Alguns servidores retornam ICY em vez de HTTP
        if response.startswith(b'ICY'):
            response = response.replace(b'ICY', b'HTTP/1.1', 1)

        # Decodifica o conteúdo com segurança
        response_text = response.decode('utf-8', errors='ignore')

        # Extrai o conteúdo entre <body> e </body>
        start = response_text.find("<body>")
        end = response_text.find("</body>")
        if start == -1 or end == -1:
            return {"current_song": "Formato inesperado"}, 200

        content = response_text[start + 6:end].strip()
        parts = content.split(',')

        # Index 6 contém a música
        if len(parts) >= 7:
            current_song = parts[6].strip()
        else:
            current_song = "Música indisponível"

        return {"current_song": current_song}, 200

    except Exception as e:
        print("❌ Erro ao buscar música atual:", e)
        return {"error": str(e)}, 500



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
