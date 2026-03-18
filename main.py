"""
CFO Buddy — Flask Server
"""

import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "data"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

ALLOWED_EXTENSIONS = {"csv", "pdf", "xlsx", "xls", "docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_response(content):
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text") or block.get("content") or ""
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts) or str(content)
    return str(content)

# ==========================
# ROUTES
# ==========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    from core import CFOBuddy
    from langchain_core.messages import HumanMessage

    data = request.get_json()
    user_input = data.get("message", "").strip()
    thread_id = data.get("thread_id", "main")

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    config = {"configurable": {"thread_id": thread_id}}

    try:
        response = CFOBuddy.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        )
        content = parse_response(response["messages"][-1].content)
        return jsonify({"response": content, "thread_id": thread_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/threads", methods=["GET"])
def get_threads():
    from core.memory import retrieve_all_threads
    try:
        threads = retrieve_all_threads()
        return jsonify({"threads": threads if threads else ["main"]})
    except Exception as e:
        return jsonify({"threads": ["main"]})


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"Supported types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    filename = secure_filename(file.filename)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    return jsonify({
        "message": f"'{filename}' uploaded! Run build_index.py to index it.",
        "filename": filename
    })


@app.route("/files", methods=["GET"])
def list_files():
    data_folder = "data"
    if not os.path.exists(data_folder):
        return jsonify({"files": []})

    files = []
    for f in os.listdir(data_folder):
        ext = os.path.splitext(f)[1].lower()
        if ext in {".csv", ".pdf", ".xlsx", ".xls", ".docx"}:
            size = os.path.getsize(os.path.join(data_folder, f))
            files.append({
                "name": f,
                "type": ext.lstrip(".").upper(),
                "size": f"{size / 1024:.1f} KB"
            })
    return jsonify({"files": files})


if __name__ == "__main__":
    app.run(debug=True, port=5000)