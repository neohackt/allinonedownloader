import os
import uuid
import subprocess
from flask import Flask, request, jsonify, send_file, render_template, abort

# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------
app = Flask(__name__, template_folder='templates', static_folder='static')
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def run_yt_dlp(cmd_list):
    """Run yt-dlp with mweb client (bypasses 429 / sign-in)."""
    try:
        proc = subprocess.run(
            cmd_list,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc.stdout, proc.stderr
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr.strip()) from e

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/info", methods=["POST"])
def info():
    url = request.json.get("url", "").strip()
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=mweb",
        url,
    ]
    try:
        stdout, _ = run_yt_dlp(cmd)
        data = stdout.splitlines()[0]
        return jsonify(eval(data))
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["POST"])
def download():
    url = request.json.get("url", "").strip()
    fmt = request.json.get("format", "bv+ba/best")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    uid = uuid.uuid4().hex
    out_template = f"{DOWNLOAD_DIR}/{uid}.%(ext)s"

    cmd = [
        "yt-dlp",
        "-f", fmt,
        "-o", out_template,
        "--no-playlist",
        "--extractor-args", "youtube:player_client=mweb",
        url,
    ]
    try:
        run_yt_dlp(cmd)
        file = next(f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(uid))
        return jsonify({"file": file})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/file/<path:name>")
def serve_file(name):
    path = os.path.join(DOWNLOAD_DIR, name)
    if not os.path.exists(path):
        abort(404)
    return send_file(path, as_attachment=True)

# ------------------------------------------------------------------------------
# Local runner
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
