// app.js
const socket = io(); 

new Vue({
    el: '#app',
    data: {
        step: 'enter_name',
        playerName: '',
        playerNameInput: '',
        nameErrorMessage: '',
        players: [],
        playerNames: {},
        connected: false,
        playerId: null,
        gameId: null,
        joinGameId: '',
        gameStarted: false,
        myChoice: null,
        scores: {},
        round: 0,
        roundResult: {},
        gameOver: false,
        winnerId: null,
        errorMessage: '', 
        globalErrorMessage: '', 
        playerDisconnectedMessage: ''
    },
    computed: {
        opponentId() {
            if (!this.gameId || !this.scores || !this.playerId) return null;
            const players = Object.keys(this.scores);
            return players.find(id => id !== this.playerId);
        },
        opponentScore() {
            return this.opponentId ? (this.scores[this.opponentId] || 0) : 0;
        },
        opponentChoice() {
            if (this.roundResult.player_choices && this.opponentId) {
                return this.roundResult.player_choices[this.opponentId];
            }
            return 'N/A';
        },
        opponentName() {
            const opponentId = this.players.find(id => id !== this.playerId);
            return opponentId ? this.playerNames[opponentId] || 'Oponente' : 'Aguardando...';
        },
    },
    methods: {
        showGlobalError(message) {
            this.globalErrorMessage = message;
            setTimeout(() => {
                this.globalErrorMessage = '';
            }, 5000); 
        },
        createGame() {
            this.errorMessage = '';
            socket.emit('create_game', { playerName: this.playerName });
        },
        joinGame() {
            this.errorMessage = '';
            if (this.joinGameId) {
                socket.emit('join_game', { 
                    game_id: this.joinGameId, 
                    playerName: this.playerName 
                });
            } else {
                this.errorMessage = 'Por favor, insira um ID de jogo.';
            }
        },
        makeChoice(choice) {
            if (!this.myChoice && !this.gameOver) { 
                this.myChoice = choice;
                this.roundResult = {};
                socket.emit('make_choice', { game_id: this.gameId, choice: choice });
            }
        },
        resetGame() {
            this.myChoice = null;
            this.roundResult = {};
            this.gameOver = false;
            this.winnerId = null;
            this.playerDisconnectedMessage = '';
            socket.emit('reset_game', { game_id: this.gameId });
        },
        submitName() {
            if (this.playerNameInput.trim().length < 3) {
                this.nameErrorMessage = 'O nome deve ter pelo menos 3 caracteres.';
                return;
            }
            this.playerName = this.playerNameInput.trim();
            this.nameErrorMessage = '';
            this.step = 'menu';
        },
    },
    created() {
        socket.on('connected', (data) => {
            this.connected = true;
            this.playerId = data.sid;
            console.log('Conectado ao servidor. Seu SID:', this.playerId);
        });

        socket.on('game_created', (data) => {
            this.gameId = data.game_id;
            this.playerId = data.player_id;
            this.players = [this.playerId]; 
            this.playerNames = { [this.playerId]: this.playerName }; 
            this.scores = { [this.playerId]: 0 };
            this.round = 0;
            this.step = 'in_game'; 
            this.gameStarted = false; 
            console.log('Jogo criado:', this.gameId);
        });

        socket.on('game_start', (data) => {
            console.log("Recebido evento 'game_start' com os dados:", data); 
            this.gameId = data.game_id;
            this.gameStarted = true;
            this.players = data.players;          
            this.playerNames = data.player_names;
            this.scores = data.scores;            
            this.round = 1;
            this.step = 'in_game';                
        });
        socket.on('round_result', (data) => {
            this.roundResult = data;
            console.log('Resultado da rodada:', data);
        });

        socket.on('update_score', (data) => {
            this.scores = data.scores;
            console.log('Placar atualizado:', this.scores);
        });

        socket.on('next_round', (data) => {
            this.myChoice = null; 
            this.round = data.round;
            console.log('Próxima rodada:', this.round);
        });

        socket.on('game_over', (data) => {
            this.gameOver = true;
            this.winnerId = data.winner_id;
            this.scores = data.scores;
            console.log('Jogo encerrado. Vencedor:', this.winnerId);
        });

        socket.on('game_reset', (data) => {
            this.scores = data.scores;
            this.round = data.round;
            this.gameOver = false;
            this.winnerId = null;
            this.myChoice = null;
            this.roundResult = {};
            this.playerDisconnectedMessage = '';
            console.log('Jogo reiniciado.');
        });

        socket.on('error', (data) => {
            if (!this.gameId) { 
                this.errorMessage = data.message;
            } else { 
                this.showGlobalError(data.message);
            }
            console.error('Erro do servidor:', data.message);
        });

        socket.on('player_disconnected', (data) => {
            this.playerDisconnectedMessage = data.message;
            this.gameStarted = false;
            this.gameOver = true; 
            this.winnerId = null; 
            console.log('Oponente desconectou:', data.message);
        });
    }
});
