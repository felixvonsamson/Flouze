from flask import Flask, Markup, request
import os.path
import datetime
from flask_socketio import SocketIO



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
