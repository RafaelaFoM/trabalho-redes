#Pedra, Papel e Tesoura

Um jogo clássico de Pedra, Papel e Tesoura implementado com uma arquitetura web moderna, permitindo que dois jogadores se enfrentem em tempo real em salas privadas.

---

## Features

* **Salas de Jogo Privadas:** Crie um jogo e receba um ID único para compartilhar com um amigo.
* **Nomes de Jogador:** Os jogadores inserem seus próprios nomes para uma experiência mais personalizada.
* **Jogabilidade em Tempo Real:** As escolhas são processadas e os resultados exibidos instantaneamente para ambos os jogadores usando WebSockets.
* **Sistema de Pontuação:** A partida continua até que um jogador atinja a pontuação máxima definida (3).
* **Interface Reativa:** Interface de usuário limpa e moderna construída com Vue.js e estilizada com Tailwind CSS.

---

## Tecnologias Utilizadas

Este projeto é dividido em duas partes principais: o backend que gerencia a lógica do jogo e o frontend que fornece a interface para o usuário.

#### **Backend**
* **Python 3:** Linguagem principal para a lógica do servidor.
* **Flask:** Micro-framework web para servir a aplicação e gerenciar as rotas.
* **Flask-SocketIO:** Para comunicação bidirecional e em tempo real entre o cliente e o servidor via WebSockets.

#### **Frontend**
* **HTML5 / CSS3:** Estrutura e estilo base da página.
* **JavaScript (ES6+):** Linguagem para a lógica do lado do cliente.
* **Vue.js (v2):** Framework JavaScript progressivo para construir a interface de usuário reativa.
* **Tailwind CSS:** Framework de CSS "utility-first" para estilização rápida e moderna.
* **Font Awesome:** Biblioteca de ícones.

---

## Estrutura do Projeto

```
/
├── server_flask.py      # Lógica do servidor Flask e SocketIO
├── requirements.txt     # Dependências do Python
└── frontend/
    ├── index.html       # O arquivo HTML principal da aplicação
    ├── app.js           # Lógica do cliente com Vue.js
    └── style.css        # Estilos CSS personalizados (se houver)
```

---

## Como Executar o Projeto

Siga os passos abaixo para executar o projeto em sua máquina local.

#### **1. Pré-requisitos**
* **Python 3.8+** instalado.
* **pip** (gerenciador de pacotes do Python).

#### **2. Clone o Repositório**
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio
```

#### **3. Crie e Ative um Ambiente Virtual (Recomendado)**
Isso mantém as dependências do projeto isoladas do seu sistema.
```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar no Windows
.\venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate
```

#### **4. Crie o arquivo `requirements.txt`**
Crie um arquivo chamado `requirements.txt` na pasta raiz do projeto e adicione o seguinte conteúdo:
```
Flask
Flask-SocketIO
eventlet
```
*(**Nota:** `eventlet` é um servidor WSGI de alta performance recomendado para Flask-SocketIO)*

#### **5. Instale as Dependências**
Com o ambiente virtual ativado, instale todas as bibliotecas necessárias com um único comando:
```bash
pip install -r requirements.txt
```

#### **6. Execute o Servidor**
```bash
python server_flask.py
```
O servidor estará rodando e acessível na sua rede local. O terminal mostrará algo como:
`* Running on http://0.0.0.0:5000/`

#### **7. Acesse a Aplicação**
* **Para jogar sozinho (em duas abas):** Abra seu navegador e acesse `http://localhost:5000`. Abra uma segunda aba no mesmo endereço.
* **Para jogar com outra pessoa na mesma rede:** Encontre o endereço IP local do seu computador (ex: `192.168.1.10`). A outra pessoa deve acessar `http://192.168.1.10:5000` no navegador dela.

---

## Futuras Melhorias

* **Sistema de Reconexão:** Permitir que um jogador que caiu por um breve período possa se reconectar à partida em andamento.
* **Animações Melhoradas:** Adicionar animações mais elaboradas para vitórias de rodada ou de jogo (ex: confetes).
* **Histórico de Partidas:** Salvar e exibir o histórico de vitórias e derrotas do jogador.

---

