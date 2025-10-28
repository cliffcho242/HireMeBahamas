from flask import Flask

app = Flask(__name__)


@app.route("/test")
def test():
    return "Hello World"


if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)
