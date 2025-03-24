from flask import Flask, Response, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
import os

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

RADIO_URL = "http://82.145.41.50:7005/;stream.mp3"

@app.route("/")
def index():
    return "🎧 Proxy de rádio online está ativo!"

@app.route("/stream")
def stream():
    try:
        print("🔁 Conectando ao servidor Shoutcast...")
        headers = {
            "User-Agent": request.headers.get("User-Agent", "Mozilla/5.0"),
            "Icy-MetaData": "1"  # Solicita os metadados ICY (opcional)
        }

        r = requests.get(RADIO_URL, headers=headers, stream=True, timeout=10)

        # Se ICY for retornado como "status", requests ainda aceita, mas o conteúdo precisa ser repassado diretamente
        def generate():
            try:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk
            except Exception as e:
                print("❌ Erro durante o stream:", e)

        print("✅ Stream conectado. Enviando áudio ao cliente.")
        return Response(generate(), content_type="audio/mpeg")

    except Exception as e:
        print("❌ Erro ao acessar rádio:", e)
        return f"Erro ao acessar rádio: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
