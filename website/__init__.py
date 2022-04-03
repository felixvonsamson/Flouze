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
  app.jinja_env.globals.update(zip=zip)
  
  global engine
  engine = gameEngine.load_data() if os.path.isfile("data.pck")  \
       else init_engine()
  
  socketio = SocketIO(app)
  engine.socketio = socketio
  @socketio.on("give_identity")
  def give_identity():
    if session["ID"] == "admin":
      engine.admin_sid = request.sid
    else:
      player = engine.players[int(session["ID"])]
      player.sid = request.sid
  @socketio.on("hide_message")
  def hide_message(message_id):
    player = engine.players[int(session["ID"])]
    player.messages[message_id][1] = datetime.datetime.now()
  @socketio.on("answer_flouze_request")
  def answer_flouze_request(accept):
    player = engine.players[int(session["ID"])]
    requester, amount = player.flouze_request
    if accept: 
      player.send_money(requester, amount, update_sender=True)
    else:
      requester.send_message(f"Votre demande à été refusée par {player.name}.")
    player.requested_flouze = None
  @socketio.on("select_color")
  def select_color(color_id):
    assert color_id in range(5)
    player = engine.players[int(session["ID"])]
    game = engine.current_game
    if game.owner[color_id] :
      if game.owner[color_id] == player :
        player.send_message("Vous avez déjà selectioné cette couleur.", 
                            category="error", persistant=False)
      else:
        player.send_message(
          f"{game.owner[color_id]['name']} a été plus rapide que vous !", 
          category="error", persistant=False)
    else:
      updates = []
      if player.color != None :
        game.owner[player.color["id"]] = None
        updates.append((player.color["name"], ""))
      player.color = game.colors[color_id]
      player.is_done = True
      updates.append((player.color["name"], player.name))
      engine.update_fields(updates)

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
