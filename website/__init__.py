from flask import Flask, Markup
import os.path
import pickle
import datetime
from flask_socketio import SocketIO

def init_player(ID, prenom, mdp):
    player = {}
    player["ID"] = ID
    player["name"] = prenom
    player["password"] = mdp
    player["flouze"] = 0
    player["saved_flouze"] = 0 # Dans le jeu 3 l'argent est mis de coté
    player["stars"] = 0
    player["color"] = "#ffffff"
    player["choix"] = None
    player["done"] = False # Indique si le joueur a fait son choix
    player["otherPlayers"] = list(range(5))
    player["otherPlayers"].remove(ID)
    return player

pages = [      # Liste des pages a afficher dans l'ordre / round est de la forme [jeu, manche]
    { "url": "Jeu1-title.html",  "round": [1, 0]},
    { "url": "Jeu1-choix.html",  "round": [1, 1], "prize": 200},
    { "url": "results.html",     "round": [1, 1]},
    { "url": "Jeu1-choix.html",  "round": [1, 2], "prize": 400},
    { "url": "results.html",     "round": [1, 2]},
    { "url": "Jeu1-choix.html",  "round": [1, 3], "prize": 600},
    { "url": "results.html",     "round": [1, 3]},
    { "url": "Jeu2-title.html",  "round": [2, 0]},
    { "url": "Jeu2-choix.html",  "round": [2, 1], "prize": 50},
    { "url": "Jeu2-reveal.html", "round": [2, 1]},
    { "url": "results.html",     "round": [2, 1]},
    { "url": "Jeu2-choix.html",  "round": [2, 2], "prize": 100},
    { "url": "Jeu2-reveal.html", "round": [2, 2]},
    { "url": "results.html",     "round": [2, 2]},
    { "url": "Jeu2-choix.html",  "round": [2, 3], "prize": 150},
    { "url": "Jeu2-reveal.html", "round": [2, 3]},
    { "url": "results.html",     "round": [2, 3]},
    { "url": "Jeu3-title.html",  "round": [3, 0], "initial_flouze": 100},
    { "url": "Jeu3-choix.html",  "round": [3, 1], "gain": 1.2},
    { "url": "results.html",     "round": [3, 1]},
    { "url": "Jeu3-choix.html",  "round": [3, 2], "gain": 1.5},
    { "url": "results.html",     "round": [3, 2]},
    { "url": "Jeu3-choix.html",  "round": [3, 3], "gain": 2},
    { "url": "results.html",     "round": [3, 3]},
    { "url": "Jeu4-title.html",  "round": [4, 0]},
    { "url": "Jeu4-choix.html",  "round": [4, 1], "prize": [[150, 100, 50, 0, "star"]]},
    { "url": "Jeu4-reveal.html", "round": [4, 1], "prize": [[150, 100, 50, 0, "star"]]},
    { "url": "results.html",     "round": [4, 1]},
    { "url": "Jeu4-choix.html",  "round": [4, 2], "prize": [[250, 150, 0, -150, "star"], [400, 250, 0, -250, "star"]]},
    { "url": "Jeu4-reveal.html", "round": [4, 2], "prize": [[250, 150, 0, -150, "star"], [400, 250, 0, -250, "star"]]},
    { "url": "results.html",     "round": [4, 2]},
    { "url": "Jeu4-choix.html",  "round": [4, 3], "prize": [[400, 200, -250, "star", "star"], [600, 250, -300, "star", "star"], [1000, 300, -400, "star", "star"]]},
    { "url": "Jeu4-reveal.html", "round": [4, 3], "prize": [[400, 200, -250, "star", "star"], [600, 250, -300, "star", "star"], [1000, 300, -400, "star", "star"]]},
    { "url": "results.html",     "round": [4, 3]},
    { "url": "donner_des_etoiles.html", "round": [0, 0]},
    { "url": "Jeu5-title.html",  "round": [5, 0], "prize": 2500, "bonus": 500},
    { "url": "Jeu 5",            "round": [5, 1]},
    { "url": "results.html",     "round": [5, 1]},
    { "url": "Jeu 5",            "round": [5, 2]},
    { "url": "results.html",     "round": [5, 2]},
    { "url": "Jeu 5",            "round": [5, 3]},
    { "url": "results.html",     "round": [5, 3]}
]

def load_data():
    with open("data.pck", 'rb') as file:
        gameState, players, log = pickle.load(file)

    return gameState, players, log

def init_game():
    players = []
    with open("players.txt", "r") as file:
        for p in range(5):
            line = file.readline().split()
            players.append(init_player(p, line[0], line[1]))
    gameState = { # évolution des status du jeu
        'iterator': 0, # pointeur pour indiquer sur quel page on est (fait réference a l'array 'pages')
        'done': 0,  # Nombre de joueurs qui ont fait leur choix
        'game4_bonus': 0, # combien de fois les joueurs ont tous choisis des objets differents
        'masterPrizeBonus': False,  # bonus pour le jeu 5
        'starMaster': None, # joueur ayant le plus d'étoiles à la fin du jeu 4
        'otherPlayers': players.copy(), # Liste des autres joueurs pour le jeu 5
        'phase': "proposition" # Indique dans quelle phase on est pour le jeu 5
    }
    return gameState, players, [datetime.datetime.now().strftime('%H:%M:%S : ') + "LE JEU A COMMENCÉ"]

gameState, players, log = load_data() if os.path.isfile("data.pck") else init_game()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    global socketio
    socketio = SocketIO(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return socketio, app
