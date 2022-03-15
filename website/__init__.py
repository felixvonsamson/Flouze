from flask import Flask, Markup, request
import os.path
import pickle
import datetime
from flask_socketio import SocketIO



def init_player(ID, prenom, mdp, color1, color2):
    player = {}
    player["ID"] = ID
    player["name"] = prenom
    player["password"] = mdp
    player["flouze"] = 0
    player["saved_flouze"] = 0 # Dans le jeu 3 l'argent est mis de coté
    player["stars"] = 0
    player["color"] = color1
    player["secColor"] = color2
    player["choix"] = None
    player["done"] = False # Indique si le joueur a fait son choix
    player["otherPlayers"] = list(range(5))
    player["otherPlayers"].remove(ID)
    player["namespace"] = None
    player["gain_a_partager"] = 0 # Quantitée a partager dans 'partager.htlm'
    return player

pages = [      # Liste des pages a afficher dans l'ordre / round est de la forme [jeu, manche]
    { "url": "title.html",       "round": [1, 0], "background": "10.jpg"},
    { "url": "Jeu1-choix.html",  "round": [1, 1], "background": "10.jpg", "prize": 200},
    { "url": "results.html",     "round": [1, 1], "background": "10.jpg"},
    { "url": "Jeu1-choix.html",  "round": [1, 2], "background": "10.jpg", "prize": 400},
    { "url": "results.html",     "round": [1, 2], "background": "10.jpg"},
    { "url": "Jeu1-choix.html",  "round": [1, 3], "background": "10.jpg", "prize": 600, "stars": 1},
    { "url": "results.html",     "round": [1, 3], "background": "10.jpg"},
    { "url": "title.html",       "round": [2, 0], "background": "9.jpg"},
    { "url": "Jeu2-choix.html",  "round": [2, 1], "background": "9.jpg", "prize": 50},
    { "url": "Jeu2-reveal.html", "round": [2, 1], "background": "9.jpg"},
    { "url": "results.html",     "round": [2, 1], "background": "9.jpg"},
    { "url": "Jeu2-choix.html",  "round": [2, 2], "background": "9.jpg", "prize": 100},
    { "url": "Jeu2-reveal.html", "round": [2, 2], "background": "9.jpg"},
    { "url": "results.html",     "round": [2, 2], "background": "9.jpg"},
    { "url": "Jeu2-choix.html",  "round": [2, 3], "background": "9.jpg", "prize": 150, "stars": 2},
    { "url": "Jeu2-reveal.html", "round": [2, 3], "background": "9.jpg"},
    { "url": "results.html",     "round": [2, 3], "background": "9.jpg"},
    { "url": "title.html",       "round": [3, 0], "background": "8.jpg", "initial_flouze": 100},
    { "url": "Jeu3-choix.html",  "round": [3, 1], "background": "8.jpg", "gain": 1.2},
    { "url": "results.html",     "round": [3, 1], "background": "8.jpg"},
    { "url": "Jeu3-choix.html",  "round": [3, 2], "background": "8.jpg", "gain": 1.5},
    { "url": "results.html",     "round": [3, 2], "background": "8.jpg"},
    { "url": "Jeu3-choix.html",  "round": [3, 3], "background": "8.jpg", "gain": 2, "stars": 2},
    { "url": "results.html",     "round": [3, 3], "background": "8.jpg"},
    { "url": "title.html",       "round": [4, 0], "background": "6.jpg"},
    { "url": "Jeu4-choix.html",  "round": [4, 1], "background": "6.jpg", "prize": [[150, 100, 50, 0, "star"]]},
    { "url": "Jeu4-reveal.html", "round": [4, 1], "background": "6.jpg", "prize": [[150, 100, 50, 0, "star"]]},
    { "url": "results.html",     "round": [4, 1], "background": "6.jpg"},
    { "url": "Jeu4-choix.html",  "round": [4, 2], "background": "6.jpg", "prize": [[250, 150, 0, -150, "star"], [400, 250, 0, -250, "star"]]},
    { "url": "Jeu4-reveal.html", "round": [4, 2], "background": "6.jpg", "prize": [[250, 150, 0, -150, "star"], [400, 250, 0, -250, "star"]]},
    { "url": "results.html",     "round": [4, 2], "background": "6.jpg"},
    { "url": "Jeu4-choix.html",  "round": [4, 3], "background": "6.jpg", "prize": [[400, 200, -250, "star", "star"], [600, 250, -300, "star", "star"], [1000, 300, -400, "star", "star"]]},
    { "url": "Jeu4-reveal.html", "round": [4, 3], "background": "6.jpg", "prize": [[400, 200, -250, "star", "star"], [600, 250, -300, "star", "star"], [1000, 300, -400, "star", "star"]]},
    { "url": "results.html",     "round": [4, 3], "background": "6.jpg"},
    { "url": "donner_des_etoiles.html", "round": [0, 0], "background": "6.jpg"},
    { "url": "results.html",     "round": [0, 1], "background": "6.jpg"},
    { "url": "title.html",       "round": [5, 0], "background": "7.jpg", "prize": 2500, "bonus": 500},
    { "url": "Jeu 5",            "round": [5, 1], "background": "7.jpg", "phase": "proposition"},
    { "url": "Jeu 5",            "round": [5, 1], "background": "7.jpg", "phase": "validation"},
    { "url": "Jeu 5",            "round": [5, 1], "background": "7.jpg", "phase": "reveal"},
    { "url": "results.html",     "round": [5, 3], "background": "7.jpg"}
]

pages_by_round = { tuple(page['round']) : page for page in pages }

theme_colors = {
    "10.jpg":["#b65612","#dfaa84"],
    "9.jpg": ["#017e68","#6ecdbc"],
    "8.jpg": ["#3f6203","#a6ca68"],
    "6.jpg": ["#024b66","#60a7c1"],
    "7.jpg": ["#6b017f","#c470d4"]
}

quiz = [
["_______ _______ _ a-t-il __ __ drapeau ______ ?",
 "_______ d’étoiles _ ____ sur __ ______ valaisan ?",
 "Combien _______ y ____ __ le _______ ______ ?"],
["Quel ____ __ enclavé ____ le _______ ?",
 "___ pays ___ ______ dans __ _______ ?",
 "___ ____ est ______ ____ __ Sénégal ?"],
["Combien _ ___ de _____ __ tram _ ________ ?",
 "_______ y ___ __ lignes __ ____ à ________ ?",
 "_______ _ a-t-il __ ____ de ____ _ Bordeaux ?"],
["Quel ____ ___ pseudo ___ ____ of ____ ?",
 "____ était ___ ______ sur ____ __ clans ?",
 "____ ____ mon _____ ___ clash __ ____ ?"],
["Comment _______ __ parc ______ _ l’université __ _______ ?",
 "________ s’appelle __ ___ adjacent _ ________ de _______ ?",
 "________ _______ le ____ ______ à _________ __ Montréal ?"],
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
            players.append(init_player(p, line[0], line[1], line[2], line[3]))
    gameState = { # évolution des status du jeu
        'iterator': 0, # pointeur pour indiquer sur quel page on est (fait réference a l'array 'pages')
        'done': 0,  # Nombre de joueurs qui ont fait leur choix
        'game4_bonus': 0, # combien de fois les joueurs ont tous choisis des objets differents
        'masterPrizeBonus': False,  # bonus pour le jeu 5
        'starMaster': None, # joueur ayant le plus d'étoiles à la fin du jeu 4
        'otherPlayers': players.copy(), # Liste des autres joueurs pour le jeu 5
        'remaining_trials': 3,
        'sabotage': False, # Sabotage du 3ème jeu si les participants sont trop coopératifs
        'questions': 0, # Indique a quel question du quiz on est
    }
    return gameState, players, [datetime.datetime.now().strftime('%H:%M:%S : ') + "LE JEU A COMMENCÉ"]

gameState, players, log = load_data() if os.path.isfile("data.pck") else init_game()

players_by_name = { p['name']: p for p in players}


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    global socketio
    socketio = SocketIO(app)
    @socketio.on('give_identity')
    def give_identity(name):
        print(f"{name} connected")
        players_by_name[name]['sid'] = request.sid

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return socketio, app
