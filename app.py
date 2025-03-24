from flask import Flask, Response, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import urllib3
import os

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

RADIO_URL = "http://82.145.41.50:7005/;stream.mp3"

@app.route("/")
def index():
    return "🎧 Proxy de rádio online com urllib3 está ativo!"

@app.route("/stream")
def stream():
    try:
        print("🔁 Conectando ao servidor Shoutcast com urllib3...")
        http = urllib3.PoolManager(headers={"User-Agent": request.headers.get("User-Agent", "")})
        resp = http.request("GET", RADIO_URL, preload_content=False)

        def generate():
            try:
                for chunk in resp.stream(1024):
                    yield chunk
            except Exception as e:
                print("❌ Erro durante o stream:", e)

        print("✅ Stream conectado com sucesso!")
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
