from flask import Flask

app = Flask(__name__)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    print("Starting ultra-minimal Flask app...")
    app.run(host="127.0.0.1", port=8009, debug=False)
