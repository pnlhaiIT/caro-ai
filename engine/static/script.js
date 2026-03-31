const SIZE = 10
let board = []
let gameOver = false
let playerTurn = true
let gameStarted = false
const boardDiv = document.getElementById("board")
const API = window.location.origin

let gameDifficulty = 0;
let currentWinCells = null

function getSelectedDifficulty() {
    const radios = document.getElementsByName("difficulty");
    for (let radio of radios) {
        if (radio.checked) return parseInt(radio.value);
    }
    return 0;
}

function setDifficultyDisabled(disabled) {
    const radios = document.getElementsByName("difficulty");
    radios.forEach(r => r.disabled = disabled);
}

function init() {
    boardDiv.innerHTML = ""

    for (let r = 0; r < SIZE; r++) {
        board[r] = []
        for (let c = 0; c < SIZE; c++) {
            board[r][c] = "."

            const cell = document.createElement("div")
            cell.classList.add("cell")

            cell.dataset.row = r
            cell.dataset.col = c

            cell.onclick = () => playerMove(r, c, cell)
            boardDiv.appendChild(cell)
        }
    }
    hideWinLine()
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
            if (currentWinCells) {
                setTimeout(() => drawWinLine(currentWinCells), 50)
            }
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
        body: JSON.stringify({
            board: board,
            difficulty: gameDifficulty
        })
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
            if (currentWinCells) {
                setTimeout(() => drawWinLine(currentWinCells), 50)
            }
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
    if (!cells || cells.length < 2) return

    currentWinCells = cells

    const boardEl = document.getElementById("board")
    const winLine = document.getElementById("winLine")

    const first = cells[0]
    const last = cells[cells.length - 1]

    const firstCell = document.querySelector(`.cell[data-row="${first[0]}"][data-col="${first[1]}"]`)
    const lastCell = document.querySelector(`.cell[data-row="${last[0]}"][data-col="${last[1]}"]`)

    if (!firstCell || !lastCell) return

    const boardRect = boardEl.getBoundingClientRect()
    const firstRect = firstCell.getBoundingClientRect()
    const lastRect = lastCell.getBoundingClientRect()

    const x1 = firstRect.left - boardRect.left + firstRect.width / 2
    const y1 = firstRect.top - boardRect.top + firstRect.height / 2

    const x2 = lastRect.left - boardRect.left + lastRect.width / 2
    const y2 = lastRect.top - boardRect.top + lastRect.height / 2

    const dx = x2 - x1
    const dy = y2 - y1
    const length = Math.sqrt(dx * dx + dy * dy)
    const angle = Math.atan2(dy, dx) * 180 / Math.PI

    winLine.style.width = `${length}px`
    winLine.style.left = `${x1}px`
    winLine.style.top = `${y1 - 3}px`
    winLine.style.transform = `rotate(${angle}deg)`
    winLine.style.display = "block"
}

function hideWinLine() {
    const winLine = document.getElementById("winLine")
    if (winLine) {
        winLine.style.display = "none"
    }
    currentWinCells = null
}

async function aiFirstMove() {
    const res = await fetch(`${API}/move`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            board: board,
            difficulty: gameDifficulty
        })
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
    board = []
    gameOver = false
    playerTurn = true
    gameStarted = false
    currentWinCells = null

    document.getElementById("winModal").style.display = "none"
    document.getElementById("turn").innerText = ""
    document.getElementById("startBtn").style.display = "inline-block"

    const radios = document.getElementsByName("difficulty")
    for (let radio of radios) {
        radio.disabled = false
    }

    document.querySelector('input[name="difficulty"][value="0"]').checked = true
    init()
}

function startGame() {
    const radios = document.getElementsByName("difficulty");
    for (let radio of radios) {
        radio.disabled = true;
    }
    gameDifficulty = getSelectedDifficulty();
    console.log("Độ khó đã chọn:", gameDifficulty);

    gameStarted = true

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

window.addEventListener("resize", () => {
    if (currentWinCells) {
        setTimeout(() => {
            drawWinLine(currentWinCells)
        }, 100)
    }
})

init()