from flask import Flask, Markup, request
import os.path
import pickle
import datetime
import config
from flask_socketio import SocketIO



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
    "________ _______ le ____ ______ à _________ __ Montréal ?"]
]



def init_game():
    players = []
    with open("players.txt", "r") as file:
        for p in range(5):
            line = file.readline().split()
            players.append(init_player(p, line[0], line[1], line[2], line[3]))
        for i, player in enumerate(players):
            player["otherPlayers"] = players.copy()
            player["otherPlayers"].pop(i)
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
        'frameId': 0, 
        'reveal': [False]*5
    }
    return gameState, players, [datetime.datetime.now().strftime('%H:%M:%S : ') + "LE JEU A COMMENCÉ"]

gameState, players, log = load_data() if os.path.isfile("data.pck") else init_game()

players_by_name = { p['name']: p for p in players }

config.admin_sid = None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    global socketio
    socketio = SocketIO(app)
    @socketio.on('give_identity')
    def give_identity(name):
        if name == "admin":
            config.admin_sid = request.sid
        else:
            players_by_name[name]['sid'] = request.sid

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return socketio, app
