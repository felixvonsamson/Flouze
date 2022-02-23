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
    player["saved_flouze"] = 0 #Dans le jeu 3 l'argent est mis de coté
    player["stars"] = 0
    player["color"] = "#ffffff"
    player["choix"] = 0 #Enregistre le choix du joueur
    player["done"] = False #Indique si le joueur a fait son choix
    player["message"] = None #Enregistre le message a afficher au joueur
    return player

pages = [      #Liste des pages a afficher dans l'ordre / id est de la forme [jeu, manche]
    { "url": "Jeu1-title.html",  "id": [1, 0]},
    { "url": "Jeu1-choix.html",  "id": [1, 1], "prize": 2000},
    { "url": "Jeu1-choix.html",  "id": [1, 2], "prize": 4000},
    { "url": "Jeu1-choix.html",  "id": [1, 3], "prize": 6000},
    { "url": "Jeu2-title.html",  "id": [2, 0]},
    { "url": "Jeu2-choix.html",  "id": [2, 1]},
    { "url": "Jeu2-reveal.html", "id": [2, 1], "prize": 500},
    { "url": "results.html",     "id": [2, 1]},
    { "url": "Jeu2-choix.html",  "id": [2, 2]},
    { "url": "Jeu2-reveal.html", "id": [2, 2], "prize": 1000},
    { "url": "results.html",     "id": [2, 2]},
    { "url": "Jeu2-choix.html",  "id": [2, 3]},
    { "url": "Jeu2-reveal.html", "id": [2, 3], "prize": 1500},
    { "url": "results.html",     "id": [2, 3]},
    { "url": "Jeu3-title.html",  "id": [3, 0], "prize": 1000},
    { "url": "Jeu3-choix.html",  "id": [3, 1], "prize": 1.2},
    { "url": "Jeu3-choix.html",  "id": [3, 2], "prize": 1.5},
    { "url": "Jeu3-choix.html",  "id": [3, 3], "prize": 2},
    { "url": "Jeu4-title.html",  "id": [4, 0]},
    { "url": "Jeu4-choix.html",  "id": [4, 1], "prize": [1500, 1000, 500, 0, "star"]},
    { "url": "Jeu4-reveal.html", "id": [4, 1], "prize": [1500, 1000, 500, 0, "star"]},
    { "url": "results.html",     "id": [4, 1]},
    { "url": "Jeu4-choix.html",  "id": [4, 2], "prize": [2500, 1500, 0, -1500, "star"]},
    { "url": "Jeu4-reveal.html", "id": [4, 2], "prize": [2500, 1500, 0, -1500, "star"]},
    { "url": "results.html",     "id": [4, 2]},
    { "url": "Jeu4-choix.html",  "id": [4, 3], "prize": [4000, 2000, -2500, "star", "star"]},
    { "url": "Jeu4-reveal.html", "id": [4, 3], "prize": [4000, 2000, -2500, "star", "star"]},
    { "url": "results.html",     "id": [4, 3]},
    { "url": "donner_des_etoiles.html", "id": [0, 0]},
    { "url": "Jeu5-title.html",  "id": [5, 0], "prize": 25000},
    { "url": "Jeu5-choix.html",  "id": [5, 1], "urlwinner": "Jeu5-choix.html", "essais": 0}
    ]

jeu4_bonus = { #les prix bonus du jeu 4 remplacerons les prix dans l'array du haut quand les joueurs choisirons tous un prix different
"prize2Bonus":  [4000, 2500, 0, -2500, "star"],
"prize3Bonus":  [6000, 2500, -3000, "star", "star"],
"prize3Double": [10000, 3000, -4000, "star", "star"]
}

iterator = None #pointeur pour indiquer sur quel page on est (fait réference a l'array 'pages')
validation = False #permet d'afficher la page de validation aux 4 joueurs concernés dans le jeu 5

def load_data():
    with open("data.pck", 'rb') as file:
        iterator, players, log = pickle.load(file)

    return iterator, players, log

def init_players():
    players = []
    with open("players.txt", "r") as file:
        for p in range(5):
            line = file.readline().split()
            players.append(init_player(p, line[0], line[1]))
    return 0, players, [datetime.datetime.now().strftime('%H:%M:%S : ') + "LE JEU A COMMENCÉ"]

iterator, players, log = load_data() if os.path.isfile("data.pck") else init_players()

done = 0 #Nobre de joueurs qui ont fait leur choix
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
