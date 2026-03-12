from flask import Flask, request, jsonify
from flask_cors import CORS

from ai import best_move

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Caro AI backend đang chạy!"

@app.route("/move", methods=["POST"])
def move():
    data = request.json
    board = data["board"]

    r,c = best_move(board)

    return jsonify({
        "row" : r,
        "col" : c 
    })

if __name__ == "__main__":
    app.run(debug=True)