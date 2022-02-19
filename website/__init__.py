from flask import Flask, Markup
import os.path
import pickle
from flask_socketio import SocketIO

def init_player(ID, prenom, mdp):
    player = {}
    player["ID"] = ID
    player["name"] = prenom
    player["password"] = mdp
    player["flouze"] = 0
    player["saved_flouze"] = 0
    player["stars"] = 0
    player["color"] = "#ffffff"
    player["choix"] = 0
    player["done"] = False
    player["message"] = None
    return player

pages = [      #Liste des pages a afficher dans l'ordre
    { "url": "Jeu1-title.html" },
    { "url": "Jeu1-choix.html", "prize": 100 },
    { "url": "Jeu1-choix.html", "prize": 200 },
    { "url": "Jeu1-choix.html", "prize": 300 },
    { "url": "Jeu2-title.html" },
    { "url": "Jeu2-choix.html"},
    { "url": "Jeu2-reveal.html"},
    { "url": "results.html", "prize": 10},
    { "url": "Jeu2-choix.html"},
    { "url": "Jeu2-reveal.html"},
    { "url": "results.html", "prize": 20},
    { "url": "Jeu2-choix.html"},
    { "url": "Jeu2-reveal.html"},
    { "url": "results.html", "prize": 30},
    { "url": "Jeu3-title.html" },
    { "url": "Jeu3-choix.html", "prize": 1.2 },
    { "url": "Jeu3-choix.html", "prize": 1.5 },
    { "url": "Jeu3-choix.html", "prize": 2 },
    { "url": "Jeu4-title.html" },
    { "url": "Jeu4-choix.html", "prize": [10, 5, 0, -1, "star"]},
    { "url": "Jeu4-reveal.html"},
    { "url": "results.html", "prize": [10, 5, 0, -1, "star"]},
    { "url": "Jeu4-choix.html", "prize": [100, 50, 0, -10, "star"], "prizeBonus": [100, 50, -10, "star", "star"]},
    { "url": "Jeu4-reveal.html"},
    { "url": "results.html", "prize": [100, 50, 0, -10, "star"], "prizeBonus": [100, 50, -10, "star", "star"]},
    { "url": "Jeu4-choix.html", "prize": [1000, 500, 0, -100, "star"], "prizeBonus": [1000, 500, -100, "star", "star"], "prizeDoubleBonus": [1000, -100, "star", "star", "star"]},
    { "url": "Jeu4-reveal.html"},
    { "url": "results.html", "prize": [1000, 500, 0, -100, "star"], "prizeBonus": [1000, 500, -100, "star", "star"], "prizeDoubleBonus": [1000, -100, "star", "star", "star"]},
    { "url": "donner_des_etoiles.html"},
    { "url": "Jeu5-title.html" },
    { "url": "Jeu5-choix.html", "urlwinner": "Jeu5-choix.html"},
    ]


bonus_jeu4 = 0 #Augmente si les joueurs choisissent tous un prix different a une manche du 4ème jeu
iterator = None #pointeur pour indiquer sur quel page on est (fait réference a l'array 'pages')

def load_data():
    with open("data.pck", 'rb') as file:
        iterator, players = pickle.load(file)
    return iterator, players

def init_players():
    players = []
    with open("players.txt", "r") as file:
        for p in range(5):
            line = file.readline().split()
            players.append(init_player(p, line[0], line[1]))
    return 0, players

iterator, players = load_data() if os.path.isfile("data.pck") else init_players()

done = 0
for i in players:
    done += i["done"]

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
