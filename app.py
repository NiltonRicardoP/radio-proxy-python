from flask import Flask, Response, stream_with_context
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Libera CORS para qualquer origem

RADIO_URL = "http://82.145.41.50:7005/;stream.mp3"

@app.route("/stream")
def proxy_stream():
    def generate():
        with requests.get(RADIO_URL, stream=True) as r:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk

    return Response(stream_with_context(generate()), content_type='audio/mpeg')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
