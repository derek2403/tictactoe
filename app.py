from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

# Define the initial board
def initialize_board():
    return [' ' for _ in range(9)]

board = initialize_board()
human_player = random.choice(['X', 'O'])
ai_player = 'O' if human_player == 'X' else 'X'
current_player = 'X'

# Check for a win
def check_win(board, player):
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), 
                      (0, 3, 6), (1, 4, 7), (2, 5, 8), 
                      (0, 4, 8), (2, 4, 6)]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] == player:
            return True
    return False

# Check for a draw
def check_draw(board):
    return ' ' not in board

# Get available moves
def get_available_moves(board):
    return [i for i, x in enumerate(board) if x == ' ']

# Minimax algorithm
def minimax(board, depth, is_maximizing, ai_player, human_player):
    if check_win(board, ai_player):
        return 1
    elif check_win(board, human_player):
        return -1
    elif check_draw(board):
        return 0
    
    if is_maximizing:
        best_score = -float('inf')
        for move in get_available_moves(board):
            board[move] = ai_player
            score = minimax(board, depth + 1, False, ai_player, human_player)
            board[move] = ' '
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for move in get_available_moves(board):
            board[move] = human_player
            score = minimax(board, depth + 1, True, ai_player, human_player)
            board[move] = ' '
            best_score = min(score, best_score)
        return best_score

# AI move
def ai_move(board, ai_player, human_player):
    best_score = -float('inf')
    best_move = None
    for move in get_available_moves(board):
        board[move] = ai_player
        score = minimax(board, 0, False, ai_player, human_player)
        board[move] = ' '
        if score > best_score:
            best_score = score
            best_move = move
    board[best_move] = ai_player

@app.route('/')
def index():
    global board
    status = ""
    if check_win(board, human_player):
        status = "You win!"
    elif check_win(board, ai_player):
        status = "AI wins!"
    elif check_draw(board):
        status = "It's a draw!"
    return render_template('index.html', board=board, status=status)

@app.route('/move/<int:cell>', methods=['POST'])
def move(cell):
    global board, current_player
    if board[cell] != ' ':
        return jsonify(success=False, message="Invalid move")
    
    if current_player == human_player:
        board[cell] = human_player
        if check_win(board, human_player):
            return jsonify(success=True, message="You win!")
        elif check_draw(board):
            return jsonify(success=True, message="It's a draw!")
        current_player = ai_player
        ai_move(board, ai_player, human_player)
        if check_win(board, ai_player):
            return jsonify(success=True, message="AI wins!")
        elif check_draw(board):
            return jsonify(success=True, message="It's a draw!")
        current_player = human_player
    return jsonify(success=True)

@app.route('/reset', methods=['POST'])
def reset():
    global board, current_player, human_player, ai_player
    board = initialize_board()
    human_player = random.choice(['X', 'O'])
    ai_player = 'O' if human_player == 'X' else 'X'
    current_player = 'X'
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
