from flask import Flask, render_template, jsonify, request, session
import random
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션을 위한 시크릿 키

# 게임 상태를 저장할 전역 변수들
game_state = {
    'is_active': False,
    'room_code': None,
    'winning_pattern': None,
    'players': {},  # {player_name: board}
    'called_numbers': set(),
    'current_number': None,
    'last_call_time': None,
    'winner': None,
}


@app.route('/')
def host_page():
    return render_template('host.html')

@app.route('/create_game', methods=['POST'])
def create_game():
    game_state['room_code'] = generate_room_code()
    game_state['winning_pattern'] = create_winning_pattern()
    game_state['is_active'] = False
    game_state['players'].clear()
    game_state['called_numbers'].clear()
    game_state['current_number'] = None
    game_state['winner'] = None
    return jsonify({
        'room_code': game_state['room_code'],
        'winning_pattern': game_state['winning_pattern']
    })

@app.route('/get_players')
def get_players():
    return jsonify({
        'players': list(game_state['players'].keys()),
        'winner': game_state.get('winner')
    })

@app.route('/start_game', methods=['POST'])
def start_game():
    if len(game_state['players']) > 0:
        game_state['is_active'] = True
        game_state['last_call_time'] = time.time()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'No players connected'})

@app.route('/play/<room_code>')
def play_page(room_code):
    if room_code != game_state['room_code']:
        return "Invalid room code", 404
    return render_template('play.html', room_code=room_code)

@app.route('/join_game', methods=['POST'])
def join_game():
    data = request.get_json()
    room_code = data.get('room_code')
    player_name = data.get('player_name')

    if room_code != game_state['room_code']:
        return jsonify({'success': False, 'message': 'Invalid room code'})

    if player_name in game_state['players']:
        return jsonify({'success': False, 'message': 'Name already taken'})

    # 새로운 플레이어 보드 생성
    game_state['players'][player_name] = {
        'board': create_bingo_board(),
        'checked': [[False]*5 for _ in range(5)]
    }

    return jsonify({
        'success': True,
        'board': game_state['players'][player_name]['board'],
        'winning_pattern': game_state['winning_pattern']
    })

@app.route('/game_status')
def game_status():
    room_code = request.args.get('room_code')
    player_name = request.args.get('player_name')

    if room_code != game_state['room_code'] or player_name not in game_state['players']:
        return jsonify({'success': False})

    return jsonify({
        'success': True,
        'is_active': game_state['is_active'],
        'current_number': game_state['current_number'],
        'called_numbers': list(game_state['called_numbers']),
        'checked': game_state['players'][player_name]['checked'],
        'winner': game_state.get('winner')
    })


@app.route('/update_numbers')
def update_numbers():
    if not game_state['is_active'] or game_state['winner']:
        return jsonify({
            'number': game_state['current_number'],
            'winner': game_state['winner'],
            'called_numbers': list(game_state['called_numbers'])
        })

    current_time = time.time()
    if (game_state['current_number'] is None or
        current_time - game_state['last_call_time'] >= 3):
        available_numbers = set(range(1, 26)) - game_state['called_numbers']
        if available_numbers:
            number = random.choice(list(available_numbers))
            game_state['current_number'] = number
            game_state['called_numbers'].add(number)
            game_state['last_call_time'] = current_time

            # 모든 플레이어의 보드 업데이트 및 승자 확인
            for player_name, player_data in game_state['players'].items():
                board = player_data['board']
                checked = player_data['checked']
                for i in range(5):
                    for j in range(5):
                        if board[i][j] == number:
                            checked[i][j] = True

                # 승자 확인
                if check_winner(player_name, checked):
                    game_state['winner'] = player_name
                    game_state['is_active'] = False

    return jsonify({
        'number': game_state['current_number'],
        'winner': game_state['winner'],
        'called_numbers': list(game_state['called_numbers'])
    })

@app.route('/get_all_boards')
def get_all_boards():
    winner = game_state.get('winner')
    return jsonify({
        'players': {
            name: {
                'board': data['board'],
                'checked': data['checked'],
                'is_winner': (name == winner)
            }
            for name, data in game_state['players'].items()
        }
    })

@app.route('/get_game_state')
def get_game_state():
    return jsonify({
        'winning_pattern': game_state['winning_pattern']
    })

def check_winner(player_name, checked):
    pattern = game_state['winning_pattern']
    for i in range(5):
        for j in range(5):
            if pattern[i][j] and not checked[i][j]:
                return False
    return True

def generate_room_code():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=6))

def create_winning_pattern():
    pattern = [[False] * 5 for _ in range(5)]
    num_true = random.randint(8, 12)
    positions = [(i, j) for i in range(5) for j in range(5)]
    selected_positions = random.sample(positions, num_true)

    for i, j in selected_positions:
        pattern[i][j] = True
    return pattern

def create_bingo_board():
    numbers = list(range(1, 26))
    random.shuffle(numbers)
    return [numbers[i:i+5] for i in range(0, 25, 5)]

if __name__ == '__main__':
    print("Server is running")
    app.run(debug=True, port=5001)
