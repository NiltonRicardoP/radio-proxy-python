from flask import Flask, Response, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import http.client
import os

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

RADIO_HOST = "82.145.41.50"
RADIO_PORT = 7005
RADIO_PATH = "/;stream.mp3"

@app.route("/")
def index():
    return "🎧 Proxy de rádio online está ativo!"

@app.route("/stream")
def stream():
    try:
        print("🔁 Conectando ao servidor Shoutcast...")
        conn = http.client.HTTPConnection(RADIO_HOST, RADIO_PORT, timeout=10)
        conn.request("GET", RADIO_PATH, headers={"User-Agent": request.headers.get("User-Agent", "")})
        resp = conn.sock.makefile("rb")

        def generate():
            try:
                while True:
                    chunk = resp.read(1024)
                    if not chunk:
                        break
                    yield chunk
            except Exception as e:
                print("❌ Erro durante o stream:", e)

        print("✅ Stream conectado. Enviando áudio ao cliente.")
        return Response(
            generate(),
            content_type="audio/mpeg",
            headers={
                "Transfer-Encoding": "chunked",
                "Connection": "keep-alive"
            }
        )

    except Exception as e:
        print("❌ Erro ao acessar rádio:", e)
        return f"Erro ao acessar rádio: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
