const SIZE = 10
let board = []
const boardDiv = document.getElementById("board")

function init() {
    for (let r = 0; r < SIZE; r++) {
        board[r] = []
        for (let c = 0; c < SIZE; c++) {
            board[r][c] = "."
            const cell = document.createElement("div")
            cell.onclick = () => playerMove(r, c, cell)
            boardDiv.appendChild(cell)
        }
    }
}

async function playerMove(r, c, cell) {
    if (board[r][c] != ".") return

    board[r][c] = "X"
    cell.innerText = "X"

    const res = await fetch("http://127.0.0.1:5000/move", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ board: board })
    })

    const data = await res.json()
    const aiCell = boardDiv.children[data.row * SIZE + data.col]

    board[data.row][data.col] = "O"
    aiCell.innerText = "O"
}
init()