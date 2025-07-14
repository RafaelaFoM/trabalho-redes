# server_flask.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__,
            static_folder='frontend',
            template_folder='frontend')

app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'
app.jinja_env.block_start_string = '{%'
app.jinja_env.block_end_string = '%}'
app.jinja_env.comment_start_string = '{#'
app.jinja_env.comment_end_string = '#}'


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

games = {}

@app.route('/')
def index():
    """Serve o arquivo HTML principal do frontend."""
    return render_template('index.html')

@socketio.on('connect')
def connect():
    """Lida com a conexão de um novo cliente."""
    print(f'Cliente conectado: {request.sid}')
    emit('connected', {'sid': request.sid})

@socketio.on('disconnect')
def disconnect():
    """Lida com a desconexão de um cliente."""
    print(f'Cliente desconectado: {request.sid}')
    for game_id in list(games.keys()):
        game = games[game_id]
        if request.sid in game['players']:
            disconnected_player_name = game['players'][request.sid]['name']
            del game['players'][request.sid] 

            if not game['players']:
                del games[game_id]
                print(f"Jogo {game_id} removido por falta de jogadores.")
            else:
                remaining_player_sid = list(game['players'].keys())[0]
                emit('player_disconnected', {'message': f'Oponente {disconnected_player_name} desconectou. O jogo terminou.'}, room=remaining_player_sid)
                del games[game_id]
                print(f"Jogo {game_id} terminado devido à desconexão de {disconnected_player_name}.")
            break

@socketio.on('create_game')
def create_game(data):
    """Cria um novo jogo e adiciona o criador com seu nome."""
    game_id = str(random.randint(10000, 99999))
    player_name = data.get('playerName', 'Jogador 1')

    games[game_id] = {
        'players': { request.sid: {'name': player_name} },
        'choices': {},
        'scores': {request.sid: 0},
        'round': 0,
        'status': 'waiting',
        'max_score': 3
    }
    join_room(game_id)
    emit('game_created', {'game_id': game_id, 'player_id': request.sid}, room=request.sid)
    print(f"Jogo {game_id} criado por {player_name} ({request.sid})")

@socketio.on('join_game')
def join_game(data):
    """Permite que um jogador se junte a um jogo existente com seu nome."""
    game_id = data.get('game_id')
    player_name = data.get('playerName', 'Jogador 2')

    if game_id in games:
        game = games[game_id]
        if len(game['players']) < 2:
            game['players'][request.sid] = {'name': player_name}
            game['scores'][request.sid] = 0
            join_room(game_id)
            game['status'] = 'playing'

            player_ids = list(game['players'].keys())
            player_names_map = {pid: pdata['name'] for pid, pdata in game['players'].items()}

            emit('game_start', {
                'game_id': game_id, 
                'players': player_ids,
                'player_names': player_names_map,
                'scores': game['scores'],
                'max_score': game['max_score']
            }, room=game_id)

            print(f"Jogador {player_name} ({request.sid}) juntou-se ao jogo {game_id}")
        else:
            emit('error', {'message': 'Jogo cheio!'}, room=request.sid)
    else:
        emit('error', {'message': 'Jogo não encontrado!'}, room=request.sid)

@socketio.on('make_choice')
def make_choice(data):
    """Registra a escolha de um jogador e verifica o resultado da rodada."""
    game_id = data.get('game_id')
    choice = data.get('choice')
    player_id = request.sid

    if game_id in games and player_id in games[game_id]['players']:
        game = games[game_id]
        if game['status'] != 'playing':
            emit('error', {'message': 'O jogo não está em andamento.'}, room=player_id)
            return

        game['choices'][player_id] = choice
        player_name = game['players'][player_id]['name']

        if len(game['choices']) == 2:
            print(f"--- CONDIÇÃO ATINGIDA: O jogo {game_id} tem 2 escolhas. Calculando resultado...")
            player1_id, player2_id = list(game['players'].keys())
            
            choice1 = game['choices'].get(player1_id)
            choice2 = game['choices'].get(player2_id)

            if choice1 and choice2:
                game['round'] += 1
                p1_name = game['players'][player1_id]['name']
                p2_name = game['players'][player2_id]['name']
                
                winner_id, message = determine_winner(choice1, choice2, player1_id, player2_id, p1_name, p2_name)

                round_result = {
                    'round': game['round'],
                    'player_choices': { player1_id: choice1, player2_id: choice2 },
                    'message': message,
                    'winner_id': winner_id
                }

                if winner_id:
                    game['scores'][winner_id] += 1

                emit('round_result', round_result, room=game_id)
                emit('update_score', {'scores': game['scores']}, room=game_id)

                if game['scores'][player1_id] >= game['max_score'] or game['scores'][player2_id] >= game['max_score']:
                    final_winner_id = player1_id if game['scores'][player1_id] >= game['max_score'] else player2_id
                    final_winner_name = game['players'][final_winner_id]['name']
                    emit('game_over', {'winner_id': final_winner_id, 'scores': game['scores']}, room=game_id)
                    game['status'] = 'finished'
                    print(f"--- JOGO TERMINADO: Jogo {game_id} terminou. Vencedor: {final_winner_name}")
                else:
                    game['choices'] = {}
                    socketio.emit('next_round', {'round': game['round'] + 1}, room=game_id)
            else:
                print(f"--- ERRO DE LÓGICA: Duas escolhas contadas, mas uma delas é inválida (choice1: {choice1}, choice2: {choice2})")
    else:
        print(f"--- ERRO DE VALIDAÇÃO: Jogada recebida de jogador/jogo inválido. GameID: {game_id}, PlayerID: {player_id}")

def determine_winner(choice1, choice2, player1_id, player2_id, p1_name, p2_name):
    """Determina o vencedor de uma rodada e usa os nomes na mensagem."""
    rules = {
        'pedra': {'tesoura'},
        'papel': {'pedra'},
        'tesoura': {'papel'}
    }

    if choice1 == choice2:
        return None, "Empate!"
    elif choice2 in rules[choice1]:
        return player1_id, f"{p1_name} venceu a rodada! ({choice1} vence {choice2})"
    else:
        return player2_id, f"{p2_name} venceu a rodada! ({choice2} vence {choice1})"
    
@socketio.on('reset_game')
def reset_game(data):
    """Reinicia um jogo existente."""
    game_id = data.get('game_id')
    if game_id in games and request.sid in games[game_id]['players']:
        game = games[game_id]
        game['choices'] = {}
        game['scores'] = {pid: 0 for pid in game['players']}
        game['round'] = 0
        game['status'] = 'playing'
        emit('game_reset', {'scores': game['scores'], 'round': game['round']}, room=game_id)
        print(f"Jogo {game_id} reiniciado.")
    else:
        emit('error', {'message': 'Não foi possível reiniciar o jogo.'}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
