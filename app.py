import os, uuid, subprocess, shlex
from flask import Flask, request, jsonify, send_file, abort

app = Flask(__name__, static_folder='static', static_url_path='')
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/info", methods=["POST"])
def info():
    url = request.json["url"]
    cmd = f"yt-dlp --dump-json --no-playlist {shlex.quote(url)}"
    try:
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.PIPE)
        data = out.splitlines()[0]
        return jsonify(eval(data))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/download", methods=["POST"])
def download():
    url = request.json["url"]
    fmt = request.json["format"]
    uid = uuid.uuid4().hex
    filename = f"{uid}.%(ext)s"
    cmd = f"yt-dlp -f {fmt} -o {shlex.quote(DOWNLOAD_DIR + '/' + filename)} --no-playlist {shlex.quote(url)}"
    try:
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE)
        file = next(f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(uid))
        return jsonify({"file": file})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/file/<path:name>")
def serve_file(name):
    path = os.path.join(DOWNLOAD_DIR, name)
    if not os.path.exists(path):
        abort(404)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
