import os.path
import datetime
from flask import Flask
from flask import redirect, url_for
from flask import request, session
from flask_socketio import SocketIO

from website.gameEngine import gameEngine

def init_engine():
  with open("players.txt", "r") as file:
    players_raw = [(player_id, *file.readline().split()) 
                   for player_id in range(5)]
  return gameEngine(players_raw)


def create_app():
  app = Flask(__name__)
  app.config["SECRET_KEY"] = "BxclfIEmzsq8HTqvFnyW"

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
  
  @socketio.on("hide_message")
  def hide_message(player_id, message_id):
    engine.players[player_id].messages[message_id][1] = datetime.datetime.now()

  from .auth import auth
  from .views import views
  from .monitoring import monitoring

  app.register_blueprint(auth, url_prefix="/")
  app.register_blueprint(views, url_prefix="/")
  app.register_blueprint(monitoring, url_prefix="/")
  
  @app.before_request
  def check_connected():
    if "ID" not in session \
       and request.endpoint not in ["auth.login", "static"]:
      return redirect(url_for("auth.login"))

  return socketio, app
