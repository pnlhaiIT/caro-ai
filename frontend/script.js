const SIZE = 10
let board = []
let gameOver = false
let playerTurn = true
const boardDiv = document.getElementById("board")

function init() {
    for (let r = 0; r < SIZE; r++) {
        board[r] = []
        for (let c = 0; c < SIZE; c++) {
            board[r][c] = "."

            const cell = document.createElement("div")
            cell.classList.add("cell")

            cell.onclick = () => playerMove(r, c, cell)
            boardDiv.appendChild(cell)
        }
    }
}

async function playerMove(r, c, cell) {

    if (gameOver || !playerTurn) return
    if (board[r][c] != ".") return

    playerTurn = false

    board[r][c] = "X"
    cell.innerText = "X"

    if (checkWin("X")) {
        alert("Bạn thắng!")
        gameOver = true
        return
    }

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

    if (checkWin("O")) {
        alert("AI thắng!")
        gameOver = true
        return
    }

    playerTurn = true
}
function checkWin(player) {
    const directions = [[1, 0], [0, 1], [1, 1], [1, -1]]
    for (let r = 0; r < SIZE; r++) {
        for (let c = 0; c < SIZE; c++) {
            if (board[r][c] != player) continue

            for (const [dr, dc] of directions) {
                let count = 0
                for (let i = 0; i < 5; i++) {
                    let nr = r + dr * i
                    let nc = c + dc * i
                    if (
                        nr >= 0 && nr < SIZE &&
                        nc >= 0 && nc < SIZE &&
                        board[nr][nc] == player
                    ) {
                        count++
                    } else break
                }
                if (count == 5) return true
            }
        }
    }
    return false
}
init()