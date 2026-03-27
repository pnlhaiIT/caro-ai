from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from ai import best_move

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/move", methods=["POST"])
def move():
    data = request.json
    board = data["board"]
    difficulty = data.get("difficulty", 0) 

    r, c = best_move(board, difficulty)  

    return jsonify({
        "row": r,
        "col": c
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=False)