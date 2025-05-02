from flask import Flask, Response
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import socket
import os
import requests

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

RADIO_HOST = '78.129.132.7'
RADIO_PORT = 4871
RADIO_PATH = '/;stream.mp3'

@app.route('/')
def index():
    return '🎧 Proxy de rádio Shoutcast com correção de cabeçalho está ativo!'

@app.route('/stream')
def stream():
    try:
        print("🔁 Iniciando proxy para o servidor Shoutcast...")

        url = f"http://{RADIO_HOST}:{RADIO_PORT}{RADIO_PATH}"
        headers = {
            "User-Agent": "RadioProxy"
        }

        def generate():
            retry_count = 0
            max_retries = 5

            while retry_count < max_retries:
                try:
                    with requests.get(url, headers=headers, stream=True, timeout=15) as r:
                        if r.status_code != 200:
                            print(f"⚠️ Código de status inesperado: {r.status_code}")
                            retry_count += 1
                            continue

                        print("✅ Streaming iniciado com sucesso")
                        for chunk in r.iter_content(chunk_size=2048):
                            if chunk:
                                yield chunk
                            else:
                                print("⚠️ Chunk vazio, pode ser corte de stream")
                        break  # finalizou sem erro? então sair

                except requests.exceptions.RequestException as err:
                    print(f"❌ Tentativa {retry_count+1} falhou: {err}")
                    retry_count += 1
                    time.sleep(2)

            print("🚫 Falha após múltiplas tentativas.")
            yield b''

        return Response(generate(), content_type="audio/mpeg")

    except Exception as e:
        print(f"❌ Erro ao configurar stream: {e}")
        return f"Erro ao acessar rádio: {e}", 500

    
@app.route("/currentsong")
def get_current_song_xml():
    try:
        url = "http://uk5freenew.listen2myradio.com:4871/admin.cgi?pass=rp15121722dj&mode=viewxml"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            return {"current_song": "Erro ao acessar XML"}, 500
        
        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)
        song = root.findtext("SONGTITLE")
        return {"current_song": song}, 200

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
