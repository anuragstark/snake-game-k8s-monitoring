from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///snake_game.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    snake_length = db.Column(db.Integer, nullable=False)
    foods_eaten = db.Column(db.Integer, nullable=False)
    game_speed = db.Column(db.Integer, nullable=False)
    canvas_size = db.Column(db.Integer, nullable=False)
    grid_size = db.Column(db.Integer, nullable=False)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Navigation Template
NAV_TEMPLATE = """
<nav class="bg-white/20 backdrop-blur-lg rounded-xl p-3 md:p-4 mb-4 md:mb-6">
    <div class="flex flex-col sm:flex-row justify-between items-center gap-3 sm:gap-4">
        <a href="/" class="text-white font-bold text-lg sm:text-xl hover:text-yellow-200 transition-colors">🐍 Snake Game</a>
        <div class="flex flex-col sm:flex-row gap-2 sm:gap-4 items-center w-full sm:w-auto">
            {% if current_user.is_authenticated %}
                <a href="/dashboard" class="text-white hover:text-yellow-200 transition-colors font-semibold text-sm sm:text-base w-full sm:w-auto text-center sm:text-left">📊 Dashboard</a>
                <span class="text-white text-sm sm:text-base">Welcome, <strong>{{ current_user.username }}</strong>!</span>
                <a href="/logout" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-semibold transition-all text-sm sm:text-base w-full sm:w-auto text-center">Logout</a>
            {% else %}
                <a href="/login" class="text-white hover:text-yellow-200 transition-colors font-semibold text-sm sm:text-base w-full sm:w-auto text-center sm:text-left">Login</a>
                <a href="/register" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold transition-all text-sm sm:text-base w-full sm:w-auto text-center">Register</a>
            {% endif %}
        </div>
    </div>
</nav>
"""

# Footer Template
FOOTER_TEMPLATE = """
<footer class="mt-8 text-center">
    <div class="bg-white/20 backdrop-blur-lg rounded-xl p-4">
        <p class="text-white/90 text-sm">Developer <strong class="text-yellow-300">Anurag stark</strong></p>
    </div>
</footer>
"""

# Game Template
GAME_TEMPLATE = """
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
<body class="bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 min-h-screen p-2 sm:p-4">
    <div class="max-w-5xl mx-auto">
        """ + NAV_TEMPLATE + """
        <div class="bg-white/10 backdrop-blur-lg rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-8 shadow-2xl">
            <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white text-center mb-4 sm:mb-6 drop-shadow-lg">🐍 Snake Game</h1>
            
            <!-- Game Controls Panel -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6">
                <!-- Speed Controls -->
                <div class="bg-white/20 rounded-xl p-3 sm:p-4">
                    <h3 class="text-white font-semibold mb-2 sm:mb-3 text-center text-sm sm:text-base">Speed Control</h3>
                    <div class="flex items-center gap-2 mb-2">
                        <button onclick="decreaseSpeed()" class="bg-red-500 hover:bg-red-600 active:bg-red-700 text-white px-4 sm:px-5 py-2 sm:py-2.5 rounded-lg font-bold transition-all text-lg min-w-[44px]">-</button>
                        <div class="flex-1 text-center">
                            <span class="text-white font-bold text-lg sm:text-xl" id="speedDisplay">5</span>
                            <p class="text-white/80 text-xs">Speed Level</p>
                        </div>
                        <button onclick="increaseSpeed()" class="bg-green-500 hover:bg-green-600 active:bg-green-700 text-white px-4 sm:px-5 py-2 sm:py-2.5 rounded-lg font-bold transition-all text-lg min-w-[44px]">+</button>
                    </div>
                    <div class="mt-2">
                        <label class="flex items-center text-white text-sm">
                            <input type="checkbox" id="autoSpeed" checked class="mr-2 w-4 h-4">
                            Auto-increase with score
                        </label>
                    </div>
                </div>

                <!-- Playground Size Controls -->
                <div class="bg-white/20 rounded-xl p-3 sm:p-4">
                    <h3 class="text-white font-semibold mb-2 sm:mb-3 text-center text-sm sm:text-base">Playground Size</h3>
                    <select id="playgroundSize" onchange="changePlaygroundSize()" class="w-full bg-white/30 text-white px-3 sm:px-4 py-2 sm:py-2.5 rounded-lg font-semibold mb-2 text-sm sm:text-base">
                        <option value="300">Small (300x300)</option>
                        <option value="400" selected>Medium (400x400)</option>
                        <option value="500">Large (500x500)</option>
                        <option value="600">Extra Large (600x600)</option>
                        <option value="700">Huge (700x700)</option>
                    </select>
                    <select id="gridSize" onchange="changeGridSize()" class="w-full bg-white/30 text-white px-3 sm:px-4 py-2 sm:py-2.5 rounded-lg font-semibold text-sm sm:text-base">
                        <option value="10">Tiny Cells</option>
                        <option value="15">Small Cells</option>
                        <option value="20" selected>Medium Cells</option>
                        <option value="25">Large Cells</option>
                    </select>
                    <p class="text-white/80 text-xs mt-2 text-center break-words">Canvas: <span id="canvasSize">400x400</span>px | Grid: <span id="gridInfo">20x20</span></p>
                </div>

                <!-- Score Display -->
                <div class="bg-white/20 rounded-xl p-3 sm:p-4">
                    <h3 class="text-white font-semibold mb-2 sm:mb-3 text-center text-sm sm:text-base">Scores</h3>
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
            <div class="flex justify-center mb-4 sm:mb-6 overflow-x-auto">
                <canvas id="gameCanvas" width="400" height="400" class="border-2 sm:border-4 border-white rounded-xl shadow-2xl bg-gray-900 max-w-full h-auto" style="max-width: min(100%, 400px);"></canvas>
            </div>

            <!-- Instructions and Controls -->
            <div class="text-center mb-4">
                <p class="text-white text-sm sm:text-base md:text-lg mb-3 sm:mb-2">Use Arrow Keys or WASD to move</p>
                <div class="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4">
                    <button onclick="restartGame()" class="bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white px-6 py-3 sm:py-3 rounded-xl font-bold transition-all shadow-lg text-sm sm:text-base min-h-[44px]">
                        🔄 Restart Game
                    </button>
                    <button onclick="pauseGame()" class="bg-yellow-500 hover:bg-yellow-600 active:bg-yellow-700 text-white px-6 py-3 sm:py-3 rounded-xl font-bold transition-all shadow-lg text-sm sm:text-base min-h-[44px]">
                        <span id="pauseBtn">⏸️ Pause</span>
                    </button>
                </div>
            </div>

            <!-- Stats -->
            <div class="bg-white/20 rounded-xl p-3 sm:p-4">
                <div class="grid grid-cols-3 gap-2 sm:gap-4 text-center">
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
        <div id="gameOver" class="hidden fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div class="bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl sm:rounded-3xl p-6 sm:p-8 md:p-10 text-center shadow-2xl transform scale-95 hover:scale-100 transition-all w-full max-w-md">
                <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-3 sm:mb-4">Game Over!</h2>
                <p class="text-white text-xl sm:text-2xl mb-2">Final Score: <span id="finalScore" class="font-bold">0</span></p>
                <p class="text-white/90 text-base sm:text-lg mb-4 sm:mb-6">Snake Length: <span id="finalLength" class="font-bold">0</span></p>
                <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
                    <button onclick="restartGame()" class="bg-white text-purple-600 px-6 sm:px-8 py-3 sm:py-4 rounded-xl font-bold text-base sm:text-lg md:text-xl hover:bg-gray-100 active:bg-gray-200 transition-all shadow-lg min-h-[44px]">
                        Play Again 🎮
                    </button>
                    <a href="/dashboard" class="bg-blue-500 text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl font-bold text-base sm:text-lg md:text-xl hover:bg-blue-600 active:bg-blue-700 transition-all shadow-lg inline-block text-center min-h-[44px] flex items-center justify-center">
                        View Dashboard 
                    </a>
                </div>
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

            async function gameOver() {
                gameRunning = false;
                finalScoreEl.textContent = score;
                finalLengthEl.textContent = snake.length;
                gameOverEl.classList.remove('hidden');
                
                // Save score to database if user is logged in
                {% if current_user.is_authenticated %}
                try {
                    const response = await fetch('/api/save_score', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            score: score,
                            snake_length: snake.length,
                            foods_eaten: foodsEaten,
                            game_speed: gameSpeed,
                            canvas_size: canvasSize,
                            grid_size: gridSize
                        })
                    });
                    const data = await response.json();
                    if (data.success) {
                        console.log('Score saved successfully!');
                    }
                } catch (error) {
                    console.error('Error saving score:', error);
                }
                {% endif %}
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
        """ + FOOTER_TEMPLATE + """
    </div>
</body>
</html>
"""

# Register Template
REGISTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - Snake Game</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 min-h-screen p-2 sm:p-4">
    <div class="max-w-md mx-auto mt-8 sm:mt-12 md:mt-20">
        """ + NAV_TEMPLATE + """
        <div class="bg-white/10 backdrop-blur-lg rounded-2xl sm:rounded-3xl p-6 sm:p-8 shadow-2xl">
            <h1 class="text-3xl sm:text-4xl font-bold text-white text-center mb-4 sm:mb-6">Create Account</h1>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="mb-4">
                        {% for message in messages %}
                            <div class="bg-red-500/80 text-white px-4 py-2 rounded-lg mb-2">{{ message }}</div>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}
            
            <form method="POST" action="/register" class="space-y-4">
                <div>
                    <label class="block text-white font-semibold mb-2">Username</label>
                    <input type="text" name="username" required class="w-full px-4 py-3 rounded-lg bg-white/30 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="Enter username">
                </div>
                <div>
                    <label class="block text-white font-semibold mb-2">Email</label>
                    <input type="email" name="email" required class="w-full px-4 py-3 rounded-lg bg-white/30 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="Enter email">
                </div>
                <div>
                    <label class="block text-white font-semibold mb-2">Password</label>
                    <input type="password" name="password" required class="w-full px-4 py-3 rounded-lg bg-white/30 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="Enter password">
                </div>
                <div>
                    <label class="block text-white font-semibold mb-2">Confirm Password</label>
                    <input type="password" name="confirm_password" required class="w-full px-4 py-3 rounded-lg bg-white/30 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="Confirm password">
                </div>
                <button type="submit" class="w-full bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white px-6 py-3 sm:py-3.5 rounded-xl font-bold text-base sm:text-lg transition-all shadow-lg min-h-[44px]">
                    Register
                </button>
            </form>
            <p class="text-white text-center mt-4 text-sm sm:text-base">
                Already have an account? <a href="/login" class="text-yellow-300 hover:text-yellow-200 font-semibold">Login here</a>
            </p>
        </div>
        """ + FOOTER_TEMPLATE + """
    </div>
</body>
</html>
"""

# Login Template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Snake Game</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 min-h-screen p-2 sm:p-4">
    <div class="max-w-md mx-auto mt-8 sm:mt-12 md:mt-20">
        """ + NAV_TEMPLATE + """
        <div class="bg-white/10 backdrop-blur-lg rounded-2xl sm:rounded-3xl p-6 sm:p-8 shadow-2xl">
            <h1 class="text-3xl sm:text-4xl font-bold text-white text-center mb-4 sm:mb-6">Login</h1>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="mb-4">
                        {% for message in messages %}
                            <div class="bg-red-500/80 text-white px-4 py-2 rounded-lg mb-2">{{ message }}</div>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}
            
            <form method="POST" action="/login" class="space-y-4">
                <div>
                    <label class="block text-white font-semibold mb-2">Username or Email</label>
                    <input type="text" name="username" required class="w-full px-4 py-3 rounded-lg bg-white/30 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="Enter username or email">
                </div>
                <div>
                    <label class="block text-white font-semibold mb-2">Password</label>
                    <input type="password" name="password" required class="w-full px-4 py-3 rounded-lg bg-white/30 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="Enter password">
                </div>
                <button type="submit" class="w-full bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white px-6 py-3 sm:py-3.5 rounded-xl font-bold text-base sm:text-lg transition-all shadow-lg min-h-[44px]">
                    Login
                </button>
            </form>
            <p class="text-white text-center mt-4 text-sm sm:text-base">
                Don't have an account? <a href="/register" class="text-yellow-300 hover:text-yellow-200 font-semibold">Register here</a>
            </p>
        </div>
        """ + FOOTER_TEMPLATE + """
    </div>
</body>
</html>
"""

# Dashboard Template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Snake Game</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 min-h-screen p-2 sm:p-4">
    <div class="max-w-6xl mx-auto">
        """ + NAV_TEMPLATE + """
        <div class="bg-white/10 backdrop-blur-lg rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-8 shadow-2xl">
            <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold text-white text-center mb-4 sm:mb-6">📊 Your Dashboard</h1>
            
            <!-- Stats Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mb-6 sm:mb-8">
                <div class="bg-yellow-500/30 rounded-xl p-6 text-center">
                    <p class="text-white/80 text-sm mb-2">Total Games Played</p>
                    <p class="text-white font-bold text-3xl">{{ total_games }}</p>
                </div>
                <div class="bg-purple-500/30 rounded-xl p-6 text-center">
                    <p class="text-white/80 text-sm mb-2">Highest Score</p>
                    <p class="text-white font-bold text-3xl">{{ highest_score }}</p>
                </div>
                <div class="bg-green-500/30 rounded-xl p-6 text-center">
                    <p class="text-white/80 text-sm mb-2">Average Score</p>
                    <p class="text-white font-bold text-3xl">{{ average_score }}</p>
                </div>
            </div>
            
            <!-- Score History -->
            <div class="bg-white/20 rounded-xl p-4 sm:p-6">
                <h2 class="text-xl sm:text-2xl font-bold text-white mb-3 sm:mb-4">Score History</h2>
                {% if scores %}
                    <!-- Mobile Card View -->
                    <div class="block md:hidden space-y-3">
                        {% for score in scores %}
                        <div class="bg-white/10 rounded-lg p-4 border border-white/20">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-yellow-300 font-bold text-lg">{{ score.score }}</span>
                                <span class="text-white/70 text-xs">{{ score.played_at.strftime('%m/%d %H:%M') }}</span>
                            </div>
                            <div class="grid grid-cols-2 gap-2 text-sm text-white/80">
                                <div>Length: <span class="text-white font-semibold">{{ score.snake_length }}</span></div>
                                <div>Foods: <span class="text-white font-semibold">{{ score.foods_eaten }}</span></div>
                                <div>Speed: <span class="text-white font-semibold">{{ score.game_speed }}ms</span></div>
                                <div>Size: <span class="text-white font-semibold">{{ score.canvas_size }}x{{ score.canvas_size }}</span></div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    <!-- Desktop Table View -->
                    <div class="hidden md:block overflow-x-auto">
                        <table class="w-full text-white">
                            <thead>
                                <tr class="border-b border-white/30">
                                    <th class="text-left py-3 px-4 text-sm">Date & Time</th>
                                    <th class="text-left py-3 px-4 text-sm">Score</th>
                                    <th class="text-left py-3 px-4 text-sm">Length</th>
                                    <th class="text-left py-3 px-4 text-sm">Foods</th>
                                    <th class="text-left py-3 px-4 text-sm">Speed</th>
                                    <th class="text-left py-3 px-4 text-sm">Size</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for score in scores %}
                                <tr class="border-b border-white/20 hover:bg-white/10 transition-colors">
                                    <td class="py-3 px-4 text-sm">{{ score.played_at.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                                    <td class="py-3 px-4 font-bold text-yellow-300">{{ score.score }}</td>
                                    <td class="py-3 px-4 text-sm">{{ score.snake_length }}</td>
                                    <td class="py-3 px-4 text-sm">{{ score.foods_eaten }}</td>
                                    <td class="py-3 px-4 text-sm">{{ score.game_speed }}ms</td>
                                    <td class="py-3 px-4 text-sm">{{ score.canvas_size }}x{{ score.canvas_size }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <div class="text-center py-8">
                        <p class="text-white/80 text-lg mb-4">No games played yet!</p>
                        <a href="/" class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg inline-block">
                            Play Your First Game 🎮
                        </a>
                    </div>
                {% endif %}
            </div>
            
            <div class="mt-4 sm:mt-6 text-center">
                <a href="/" class="bg-green-500 hover:bg-green-600 active:bg-green-700 text-white px-6 py-3 sm:py-3.5 rounded-xl font-bold transition-all shadow-lg inline-block text-sm sm:text-base min-h-[44px] flex items-center justify-center">
                    Play Game 🐍
                </a>
            </div>
        </div>
        """ + FOOTER_TEMPLATE + """
    </div>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    return render_template_string(GAME_TEMPLATE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return render_template_string(REGISTER_TEMPLATE)
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return render_template_string(REGISTER_TEMPLATE)
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
            return render_template_string(REGISTER_TEMPLATE)
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template_string(REGISTER_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first() or User.query.filter_by(email=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password!')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.played_at.desc()).limit(50).all()
    total_games = Score.query.filter_by(user_id=current_user.id).count()
    
    if total_games > 0:
        highest_score = db.session.query(db.func.max(Score.score)).filter_by(user_id=current_user.id).scalar()
        average_score = round(db.session.query(db.func.avg(Score.score)).filter_by(user_id=current_user.id).scalar(), 1)
    else:
        highest_score = 0
        average_score = 0
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                 scores=scores,
                                 total_games=total_games,
                                 highest_score=highest_score,
                                 average_score=average_score)

@app.route('/api/save_score', methods=['POST'])
@login_required
def save_score():
    try:
        data = request.get_json()
        score = Score(
            user_id=current_user.id,
            score=data.get('score', 0),
            snake_length=data.get('snake_length', 0),
            foods_eaten=data.get('foods_eaten', 0),
            game_speed=data.get('game_speed', 100),
            canvas_size=data.get('canvas_size', 400),
            grid_size=data.get('grid_size', 20)
        )
        db.session.add(score)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Score saved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# Initialize database
with app.app_context():
    # Ensure data directory exists for database
    import os
    db_path = app.config['SQLALCHEMY_DATABASE_URI']
    if db_path.startswith('sqlite:///'):
        # sqlite:/// means absolute path, so remove sqlite:/// to get the path
        db_file = db_path.replace('sqlite:///', '/')
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            # Set permissions to ensure writable
            os.chmod(db_dir, 0o755)
    db.create_all()

if __name__ == '__main__':
    # Development server - use Gunicorn in production (see Dockerfile)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
