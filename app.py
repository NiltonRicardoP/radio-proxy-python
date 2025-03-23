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
        resp = conn.getresponse()

        if resp.status != 200 and resp.reason != "OK":
            return f"Erro ao acessar rádio: {resp.status} {resp.reason}", 500

        print("✅ Stream recebido com sucesso")
        return Response(resp, content_type=resp.getheader("Content-Type"))

    except Exception as e:
        print("❌ Erro ao acessar rádio:", e)
        return f"Erro ao acessar rádio: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
