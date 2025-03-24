from flask import Flask, Response, request
from flask_cors import CORS
import socket
import os

app = Flask(__name__)
CORS(app)

RADIO_HOST = "82.145.41.50"
RADIO_PORT = 7005
RADIO_PATH = "/;stream.mp3"

@app.route("/")
def index():
    return "🎧 Proxy de rádio socket ativo!"

@app.route("/stream")
def stream():
    def generate():
        try:
            print("🔁 Abrindo conexão com o servidor Shoutcast...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RADIO_HOST, RADIO_PORT))

            headers = (
                f"GET {RADIO_PATH} HTTP/1.0\r\n"
                f"Host: {RADIO_HOST}\r\n"
                f"User-Agent: {request.headers.get('User-Agent', 'PythonProxy')}\r\n"
                f"Icy-MetaData: 1\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            )
            s.sendall(headers.encode())

            # Ignorar cabeçalhos (terminam em \r\n\r\n)
            buffer = b""
            while b"\r\n\r\n" not in buffer:
                buffer += s.recv(1)

            print("✅ Cabeçalho ICY recebido. Transmitindo áudio...")

            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                yield chunk
        except Exception as e:
            print("❌ Erro no stream:", e)
            yield b''

    return Response(generate(), content_type="audio/mpeg")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
