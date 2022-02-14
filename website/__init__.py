from flask import Flask
import os.path
import pickle
from flask_socketio import SocketIO

def init_player(ID, prenom, mdp):
    player = {}
    player["ID"] = ID
    player["name"] = prenom
    player["password"] = mdp
    player["flouze"] = 0
    player["stars"] = 0
    player["color"] = "#ffffff"
    player["choix"] = 0
    player["done"] = False
    player["message"] = None
    return player

pages = ["Jeu1-title.html", "Jeu1-choix.html", "Jeu1-choix.html", "Jeu1-choix.html",
    "Jeu2-choix.html", "Jeu2-reveal.html", "Jeu3-choix.html", "Jeu4-choix.html", "Jeu5-choix.html"]
prizes = [0, 100, 200, 300, 100, 100, 100, 100]
iterator = None

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
