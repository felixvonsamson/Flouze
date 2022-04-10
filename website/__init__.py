import os.path
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
  
  engine = gameEngine.load_data() if os.path.isfile("data.pck")  \
       else init_engine()
  app.config["engine"] = engine

  socketio = SocketIO(app)
  engine.socketio = socketio
  
  from .socketio_handlers import add_handlers
  add_handlers(socketio=socketio, engine=engine)

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
  @app.after_request
  def add_header(response):
    return response
    if request.endpoint == "static":
      response.cache_control.no_cache = None
      response.cache_control.private = True
      response.cache_control.max_age = 604800
    return response

  return socketio, app
