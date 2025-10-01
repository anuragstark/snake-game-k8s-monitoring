from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snake Game</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .pulse-animation {
            animation: pulse 2s ease-in-out infinite;
        }
    </style>
</head>
<body class="bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 min-h-screen flex items-center justify-center p-4">
    <div class="bg-white/10 backdrop-blur-lg rounded-3xl p-8 shadow-2xl max-w-4xl w-full">
        <h1 class="text-5xl font-bold text-white text-center mb-6 drop-shadow-lg">🐍 Snake Game</h1>
        
        <!-- Game Controls Panel -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <!-- Speed Controls -->
            <div class="bg-white/20 rounded-xl p-4">
                <h3 class="text-white font-semibold mb-3 text-center">Speed Control</h3>
                <div class="flex items-center gap-2 mb-2">
                    <button onclick="decreaseSpeed()" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-bold transition-all">-</button>
                    <div class="flex-1 text-center">
                        <span class="text-white font-bold text-xl" id="speedDisplay">5</span>
                        <p class="text-white/80 text-xs">Speed Level</p>
                    </div>
                    <button onclick="increaseSpeed()" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-bold transition-all">+</button>
                </div>
                <div class="mt-2">
                    <label class="flex items-center text-white text-sm">
                        <input type="checkbox" id="autoSpeed" checked class="mr-2 w-4 h-4">
                        Auto-increase with score
                    </label>
                </div>
            </div>

            <!-- Playground Size Controls -->
            <div class="bg-white/20 rounded-xl p-4">
                <h3 class="text-white font-semibold mb-3 text-center">Playground Size</h3>
                <select id="playgroundSize" onchange="changePlaygroundSize()" class="w-full bg-white/30 text-white px-4 py-2 rounded-lg font-semibold mb-2">
                    <option value="300">Small (300x300)</option>
                    <option value="400" selected>Medium (400x400)</option>
                    <option value="500">Large (500x500)</option>
                    <option value="600">Extra Large (600x600)</option>
                    <option value="700">Huge (700x700)</option>
                </select>
                <select id="gridSize" onchange="changeGridSize()" class="w-full bg-white/30 text-white px-4 py-2 rounded-lg font-semibold">
                    <option value="10">Tiny Cells</option>
                    <option value="15">Small Cells</option>
                    <option value="20" selected>Medium Cells</option>
                    <option value="25">Large Cells</option>
                </select>
                <p class="text-white/80 text-xs mt-2 text-center">Canvas: <span id="canvasSize">400x400</span>px | Grid: <span id="gridInfo">20x20</span></p>
            </div>

            <!-- Score Display -->
            <div class="bg-white/20 rounded-xl p-4">
                <h3 class="text-white font-semibold mb-3 text-center">Scores</h3>
                <div class="space-y-2">
                    <div class="bg-yellow-500/30 rounded-lg p-2 text-center">
                        <p class="text-white/80 text-xs">Current Score</p>
                        <p class="text-white font-bold text-2xl" id="score">0</p>
                    </div>
                    <div class="bg-purple-500/30 rounded-lg p-2 text-center">
                        <p class="text-white/80 text-xs">High Score</p>
                        <p class="text-white font-bold text-2xl" id="highScore">0</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Game Canvas -->
        <div class="flex justify-center mb-6">
            <canvas id="gameCanvas" width="400" height="400" class="border-4 border-white rounded-xl shadow-2xl bg-gray-900"></canvas>
        </div>

        <!-- Instructions and Controls -->
        <div class="text-center mb-4">
            <p class="text-white text-lg mb-2">Use Arrow Keys or WASD to move</p>
            <div class="flex justify-center gap-4 flex-wrap">
                <button onclick="restartGame()" class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg">
                    🔄 Restart Game
                </button>
                <button onclick="pauseGame()" class="bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg">
                    <span id="pauseBtn">⏸️ Pause</span>
                </button>
            </div>
        </div>

        <!-- Stats -->
        <div class="bg-white/20 rounded-xl p-4">
            <div class="grid grid-cols-3 gap-4 text-center">
                <div>
                    <p class="text-white/80 text-sm">Length</p>
                    <p class="text-white font-bold text-xl" id="snakeLength">1</p>
                </div>
                <div>
                    <p class="text-white/80 text-sm">Current Speed</p>
                    <p class="text-white font-bold text-xl" id="currentSpeed">100</p>
                </div>
                <div>
                    <p class="text-white/80 text-sm">Foods Eaten</p>
                    <p class="text-white font-bold text-xl" id="foodsEaten">0</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Game Over Modal -->
    <div id="gameOver" class="hidden fixed inset-0 bg-black/80 flex items-center justify-center z-50">
        <div class="bg-gradient-to-br from-purple-600 to-pink-600 rounded-3xl p-10 text-center shadow-2xl transform scale-95 hover:scale-100 transition-all">
            <h2 class="text-5xl font-bold text-white mb-4">Game Over!</h2>
            <p class="text-white text-2xl mb-2">Final Score: <span id="finalScore" class="font-bold">0</span></p>
            <p class="text-white/90 text-lg mb-6">Snake Length: <span id="finalLength" class="font-bold">0</span></p>
            <button onclick="restartGame()" class="bg-white text-purple-600 px-8 py-4 rounded-xl font-bold text-xl hover:bg-gray-100 transition-all shadow-lg">
                Play Again 🎮
            </button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');
        const highScoreEl = document.getElementById('highScore');
        const gameOverEl = document.getElementById('gameOver');
        const finalScoreEl = document.getElementById('finalScore');
        const finalLengthEl = document.getElementById('finalLength');
        const speedDisplayEl = document.getElementById('speedDisplay');
        const currentSpeedEl = document.getElementById('currentSpeed');
        const snakeLengthEl = document.getElementById('snakeLength');
        const foodsEatenEl = document.getElementById('foodsEaten');
        const canvasSizeEl = document.getElementById('canvasSize');
        const gridInfoEl = document.getElementById('gridInfo');
        const autoSpeedCheckbox = document.getElementById('autoSpeed');

        let canvasSize = 400;
        let gridSize = 20;
        let tileCount = canvasSize / gridSize;

        let snake = [{x: 10, y: 10}];
        let dx = 0;
        let dy = 0;
        let food = {x: 15, y: 15};
        let score = 0;
        let foodsEaten = 0;
        let highScore = localStorage.getItem('snakeHighScore') || 0;
        let gameRunning = true;
        let gamePaused = false;
        let baseSpeed = 5;
        let gameSpeed = 100;
        let lastUpdateTime = 0;

        highScoreEl.textContent = highScore;
        updateSpeedDisplay();
        gridInfoEl.textContent = tileCount + 'x' + tileCount;

        function drawGame(timestamp) {
            if (!gameRunning) return;
            if (gamePaused) {
                requestAnimationFrame(drawGame);
                return;
            }

            if (timestamp - lastUpdateTime < gameSpeed) {
                requestAnimationFrame(drawGame);
                return;
            }

            lastUpdateTime = timestamp;
            moveSnake();
            
            if (checkCollision()) {
                gameOver();
                return;
            }

            clearCanvas();
            drawFood();
            drawSnake();
            
            requestAnimationFrame(drawGame);
        }

        function clearCanvas() {
            ctx.fillStyle = '#111827';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.strokeStyle = '#1f2937';
            ctx.lineWidth = 0.5;
            for (let i = 0; i < tileCount; i++) {
                ctx.beginPath();
                ctx.moveTo(i * gridSize, 0);
                ctx.lineTo(i * gridSize, canvas.height);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(0, i * gridSize);
                ctx.lineTo(canvas.width, i * gridSize);
                ctx.stroke();
            }
        }

        function drawSnake() {
            snake.forEach((segment, index) => {
                const gradient = ctx.createLinearGradient(
                    segment.x * gridSize, segment.y * gridSize,
                    segment.x * gridSize + gridSize, segment.y * gridSize + gridSize
                );
                
                if (index === 0) {
                    gradient.addColorStop(0, '#10b981');
                    gradient.addColorStop(1, '#059669');
                } else {
                    gradient.addColorStop(0, '#34d399');
                    gradient.addColorStop(1, '#10b981');
                }
                
                ctx.fillStyle = gradient;
                ctx.fillRect(segment.x * gridSize + 1, segment.y * gridSize + 1, gridSize - 2, gridSize - 2);
                
                if (index === 0) {
                    ctx.fillStyle = 'white';
                    const eyeSize = Math.max(2, gridSize / 8);
                    const eyeOffset = gridSize / 4;
                    ctx.fillRect(segment.x * gridSize + eyeOffset, segment.y * gridSize + eyeOffset, eyeSize, eyeSize);
                    ctx.fillRect(segment.x * gridSize + gridSize - eyeOffset - eyeSize, segment.y * gridSize + eyeOffset, eyeSize, eyeSize);
                }
            });
            snakeLengthEl.textContent = snake.length;
        }

        function moveSnake() {
            if (dx === 0 && dy === 0) return;

            const head = {x: snake[0].x + dx, y: snake[0].y + dy};
            snake.unshift(head);

            if (head.x === food.x && head.y === food.y) {
                score++;
                foodsEaten++;
                scoreEl.textContent = score;
                foodsEatenEl.textContent = foodsEaten;
                
                if (score > highScore) {
                    highScore = score;
                    highScoreEl.textContent = highScore;
                    localStorage.setItem('snakeHighScore', highScore);
                }
                
                if (autoSpeedCheckbox.checked && foodsEaten % 3 === 0) {
                    baseSpeed = Math.min(10, baseSpeed + 1);
                    updateSpeedDisplay();
                    calculateGameSpeed();
                }
                
                generateFood();
            } else {
                snake.pop();
            }
        }

        function drawFood() {
            const gradient = ctx.createRadialGradient(
                food.x * gridSize + gridSize / 2, food.y * gridSize + gridSize / 2, 0,
                food.x * gridSize + gridSize / 2, food.y * gridSize + gridSize / 2, gridSize / 2
            );
            gradient.addColorStop(0, '#ef4444');
            gradient.addColorStop(1, '#dc2626');
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(food.x * gridSize + gridSize / 2, food.y * gridSize + gridSize / 2, gridSize / 2 - 2, 0, Math.PI * 2);
            ctx.fill();
        }

        function generateFood() {
            food = {
                x: Math.floor(Math.random() * tileCount),
                y: Math.floor(Math.random() * tileCount)
            };
            
            for (let segment of snake) {
                if (segment.x === food.x && segment.y === food.y) {
                    generateFood();
                    break;
                }
            }
        }

        function checkCollision() {
            const head = snake[0];
            
            if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
                return true;
            }
            
            for (let i = 1; i < snake.length; i++) {
                if (head.x === snake[i].x && head.y === snake[i].y) {
                    return true;
                }
            }
            
            return false;
        }

        function gameOver() {
            gameRunning = false;
            finalScoreEl.textContent = score;
            finalLengthEl.textContent = snake.length;
            gameOverEl.classList.remove('hidden');
        }

        function restartGame() {
            snake = [{x: Math.floor(tileCount / 2), y: Math.floor(tileCount / 2)}];
            dx = 0;
            dy = 0;
            score = 0;
            foodsEaten = 0;
            baseSpeed = 5;
            scoreEl.textContent = score;
            foodsEatenEl.textContent = foodsEaten;
            gameRunning = true;
            gamePaused = false;
            gameOverEl.classList.add('hidden');
            updateSpeedDisplay();
            calculateGameSpeed();
            generateFood();
            requestAnimationFrame(drawGame);
        }

        function pauseGame() {
            gamePaused = !gamePaused;
            document.getElementById('pauseBtn').textContent = gamePaused ? '▶️ Resume' : '⏸️ Pause';
        }

        function increaseSpeed() {
            baseSpeed = Math.min(10, baseSpeed + 1);
            updateSpeedDisplay();
            calculateGameSpeed();
        }

        function decreaseSpeed() {
            baseSpeed = Math.max(1, baseSpeed - 1);
            updateSpeedDisplay();
            calculateGameSpeed();
        }

        function updateSpeedDisplay() {
            speedDisplayEl.textContent = baseSpeed;
        }

        function calculateGameSpeed() {
            gameSpeed = Math.max(30, 200 - (baseSpeed * 15));
            currentSpeedEl.textContent = gameSpeed + 'ms';
        }

        function changeGridSize() {
            const newGridSize = parseInt(document.getElementById('gridSize').value);
            gridSize = newGridSize;
            tileCount = Math.floor(canvasSize / gridSize);
            canvasSizeEl.textContent = canvasSize + 'x' + canvasSize;
            gridInfoEl.textContent = tileCount + 'x' + tileCount;
            restartGame();
        }

        function changePlaygroundSize() {
            canvasSize = parseInt(document.getElementById('playgroundSize').value);
            canvas.width = canvasSize;
            canvas.height = canvasSize;
            tileCount = Math.floor(canvasSize / gridSize);
            canvasSizeEl.textContent = canvasSize + 'x' + canvasSize;
            gridInfoEl.textContent = tileCount + 'x' + tileCount;
            restartGame();
        }

        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowUp':
                case 'w':
                case 'W':
                    if (dy === 0) { dx = 0; dy = -1; }
                    e.preventDefault();
                    break;
                case 'ArrowDown':
                case 's':
                case 'S':
                    if (dy === 0) { dx = 0; dy = 1; }
                    e.preventDefault();
                    break;
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    if (dx === 0) { dx = -1; dy = 0; }
                    e.preventDefault();
                    break;
                case 'ArrowRight':
                case 'd':
                case 'D':
                    if (dx === 0) { dx = 1; dy = 0; }
                    e.preventDefault();
                    break;
                case ' ':
                    pauseGame();
                    e.preventDefault();
                    break;
            }
        });

        calculateGameSpeed();
        requestAnimationFrame(drawGame);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)