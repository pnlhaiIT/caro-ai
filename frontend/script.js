const SIZE = 10
let board = []
let gameOver = false
let playerTurn = true
let gameStarted = false
const boardDiv = document.getElementById("board")
const API = "http://localhost:5000"

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
    if (gameOver || !playerTurn || !gameStarted) return
    if (board[r][c] != ".") return

    playerTurn = false
    document.getElementById("turn").innerText = "Đến lượt AI...🤖"
    board[r][c] = "X"
    cell.innerText = "X"
    cell.classList.add("x")

    let winCells = checkWin("X")

    if (winCells) {

        gameOver = true
        drawWinLine(winCells)

        setTimeout(() => {
            showModal("🎉 Bạn thắng! 🏆")
        }, 800)
        return
    }
    if (checkDraw()) {
        gameOver = true
        setTimeout(() => {
            showModal("🤝 Hòa rồi! 😅")
        }, 800)
        return
    }

    const res = await fetch(`${API}/move`, {
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
    aiCell.classList.add("o")

    winCells = checkWin("O")

    if (winCells) {

        gameOver = true
        drawWinLine(winCells)

        setTimeout(() => {
            showModal("🎉 AI thắng! 🏆!")
        }, 800)

        return
    } if (checkDraw()) {
        gameOver = true
        setTimeout(() => {
            showModal("🤝 Hòa rồi! 😅")
        }, 800)
        return
    }
    playerTurn = true
    document.getElementById("turn").innerText = "Đến lượt bạn...😎"
}

function checkWin(player) {
    const directions = [
        [1, 0], [0, 1], [1, 1], [1, -1]
    ]
    for (let r = 0; r < 10; r++) {
        for (let c = 0; c < 10; c++) {
            if (board[r][c] !== player) continue

            for (let [dr, dc] of directions) {
                let cells = [[r, c]]
                for (let k = 1; k < 5; k++) {
                    let nr = r + dr * k
                    let nc = c + dc * k
                    if (nr < 0 || nr >= 10 || nc < 0 || nc >= 10) break
                    if (board[nr][nc] !== player) break
                    cells.push([nr, nc])
                }
                if (cells.length === 5) {
                    return cells
                }
            }
        }
    }
    return null
}

function checkDraw() {
    for (let r = 0; r < SIZE; r++) {
        for (let c = 0; c < SIZE; c++) {
            if (board[r][c] === ".") {
                return false
            }
        }
    }
    return true
}

function drawWinLine(cells) {
    const boardEl = document.getElementById("board")

    const first = cells[0]
    const last = cells[cells.length - 1]

    const cellSize = 40

    const x1 = first[1] * cellSize + cellSize / 2
    const y1 = first[0] * cellSize + cellSize / 2

    const x2 = last[1] * cellSize + cellSize / 2
    const y2 = last[0] * cellSize + cellSize / 2

    const length = Math.hypot(x2 - x1, y2 - y1)
    const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI

    const line = document.createElement("div")

    line.style.position = "absolute"
    line.style.left = x1 + "px"
    line.style.top = y1 + "px"
    line.style.width = length + "px"
    line.style.height = "6px"
    line.style.background = "linear-gradient(90deg,#ff4d4d,#ff0000)"
    line.style.borderRadius = "6px"
    line.style.boxShadow = "0 0 10px rgba(196, 31, 174, 0.7)"
    line.style.transform = `rotate(${angle}deg)`
    line.style.transformOrigin = "0 0"

    boardEl.appendChild(line)
}

async function aiFirstMove() {
    const res = await fetch(`${API}/move`, {
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
    aiCell.classList.add("o")

    playerTurn = true
    document.getElementById("turn").innerText = "Đến lượt bạn 😎"
}

function showModal(text) {
    document.getElementById("modalText").innerText = text
    document.getElementById("winModal").style.display = "flex"
}

function restartGame() {
    location.reload()
}

function startGame() {
    gameStarted = true
    document.getElementById("board").innerHTML = ""
    init()
    const first = Math.random() < 0.5
    if (first) {
        playerTurn = true
        document.getElementById("turn").innerText = "Bạn đi trước 😎"
    } else {
        playerTurn = false
        document.getElementById("turn").innerText = "AI đi trước 🤖"
        aiFirstMove()
    }
    document.getElementById("startBtn").style.display = "none"
}
init()