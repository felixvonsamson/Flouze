import os.path
from flask import Flask, request
from flask_socketio import SocketIO

from website.gameEngine import gameEngine

def init_engine():
    with open("players.txt", "r") as file:
        players_raw = [(player_id, *file.readline().split()) 
                       for player_id in range(5)]
    return gameEngine(players_raw)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "hjshjhdjah kjshkjdhjs"

    global engine
    engine = gameEngine.load_data() if os.path.isfile("data.pck")  \
             else init_engine()
    
    socketio = SocketIO(app)
    engine.socketio = socketio
    @socketio.on("give_identity")
    def give_identity(name):
        if name == "admin":
            engine.admin_sid = request.sid
        else:
            engine.players_by_name[name].sid = request.sid

    from .auth import auth
    from .views import views
    from .monitoring import monitoring

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(monitoring, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return socketio, app
