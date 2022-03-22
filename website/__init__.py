from flask import Flask, Markup, request
import os.path
import datetime
from flask_socketio import SocketIO





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
        players_raw = [(player_id, *file.readline().split()) for player_id in range(5)]

    return gameState, players, [datetime.datetime.now().strftime('%H:%M:%S : ') + "LE JEU A COMMENCÉ"]

gameState, players, log = load_data() if os.path.isfile("data.pck") else init_game()

players_by_name = { player.name for player in players }

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    global socketio
    socketio = SocketIO(app)
    @socketio.on('give_identity')
    def give_identity(name):
        if name == "admin":
            admin_sid = request.sid
        else:
            players_by_name[name]['sid'] = request.sid

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return socketio, app
