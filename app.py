import os
import uuid
import subprocess
import shlex
from flask import Flask, request, jsonify, send_file, render_template, abort

# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------
app = Flask(__name__, template_folder='templates', static_folder='static')
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------
@app.route("/")
def home():
    """Serve the Gen-Z downloader UI."""
    return render_template("index.html")

@app.route("/info", methods=["POST"])
def info():
    """Return JSON metadata for a URL (yt-dlp --dump-json)."""
    url = request.json.get("url", "").strip()
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    cmd = f"yt-dlp --dump-json --no-playlist {shlex.quote(url)}"
    try:
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.PIPE)
        data = out.splitlines()[0]
        return jsonify(eval(data))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["POST"])
def download():
    """Download the selected format and return a direct file link."""
    url = request.json.get("url", "").strip()
    fmt = request.json.get("format", "bv+ba/best")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    uid = uuid.uuid4().hex
    filename = f"{uid}.%(ext)s"
    cmd = (
        f"yt-dlp -f {shlex.quote(fmt)} "
        f"-o {shlex.quote(DOWNLOAD_DIR + '/' + filename)} "
        f"--no-playlist {shlex.quote(url)}"
    )

    try:
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE)
        file = next(f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(uid))
        return jsonify({"file": file})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/file/<path:name>")
def serve_file(name):
    """Serve finished downloads directly."""
    path = os.path.join(DOWNLOAD_DIR, name)
    if not os.path.exists(path):
        abort(404)
    return send_file(path, as_attachment=True)

# ------------------------------------------------------------------------------
# Entry point (only used when running locally)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
