import datetime
import pickle
import secrets
import logging

from .players import Player

from .games import Colors, Game1, Game2, Game3, Game4, Game5
from .pages_ordering import pages
from .html_icons import icons

class gameEngine(object):
  pages = pages

  def __init__(engine, players_raw):
    engine.socketio = None
    engine.admin_sid = None

    engine.logger = logging.getLogger("Flouze")
    engine.init_logger()
    engine.logs = []
    engine.nonces = set()

    engine.players = [Player(*player_raw, engine)
              for player_raw in players_raw]
    for i, player in enumerate(engine.players):
      player.other_players = engine.players.copy()
      player.other_players.pop(i)
    engine.players_by_name = { player.name:player for player in engine.players }

    engine.games = [
      Colors(engine),
      Game1(engine),
      Game2(engine),
      Game3(engine),
      Game4(engine),
      Game5(engine)
    ]

    # pointeur pour indiquer sur quelle page on est (l'array 'pages')
    engine.iterator = 0
    
    engine.log("LE JEU A COMMENCÉ !")

  def init_logger(engine):
    engine.logger.setLevel(logging.INFO)
    s_handler = logging.StreamHandler()
    s_handler.setLevel(logging.INFO)
    engine.logger.addHandler(s_handler)

  def get_nonce(engine):
    while True:
      nonce = secrets.token_hex(16)
      if nonce not in engine.nonces:
        return nonce
  
  def use_nonce(engine, nonce):
    if nonce in engine.nonces:
      return False
    engine.nonces.add(nonce)
    return True

  @property
  def current_page(engine):
    return gameEngine.pages[engine.iterator]

  @property
  def current_stage(engine):
    return gameEngine.pages[engine.iterator]["stage"]
  
  @property
  def current_game_nb(engine):
    assert (engine.current_stage[0] in range(6))
    return engine.current_stage[0]
  
  @property
  def current_game(engine):
    assert (engine.current_stage[0] in range(6))
    return engine.games[engine.current_stage[0]]

  def goto_page(engine, page_id):
    engine.iterator = page_id
    stage = engine.current_stage
    engine.log(
      f"Saut à la page : {engine.current_page['url']} "\
      f"(jeu {stage[0]}, manche {stage[1]})")
    engine.force_refresh()

  def passive_previous_page(engine):
    engine.iterator -= 1
    stage = engine.current_stage
    engine.log(
      f"Retour à la page précédante : {engine.current_page['url']} "\
      f"(jeu {stage[0]}, manche {stage[1]})")
    engine.force_refresh()

  def passive_next_page(engine):
    engine.iterator += 1
    stage = engine.current_stage
    engine.log(
      f"Passage passif à la page suivante : {engine.current_page['url']} "\
      f"(jeu {stage[0]}, manche {stage[1]})")
    engine.force_refresh()
  
  def next_page(engine, refresh=True):
    engine.iterator += 1
    stage = engine.current_stage
    page = engine.current_page
    engine.log(
      f"Passage à la page suivante : {page['url']} "\
      f"(jeu {stage[0]}, manche {stage[1]})")

    current_game_nb, current_round_nb = engine.current_stage
    if engine.current_stage == (1, 0):
      engine.games[0].end()
    elif engine.current_stage == (3, 0):
      engine.games[3].start()
    elif engine.current_stage == (4, 0):
      engine.games[3].end()
    elif current_game_nb == 5 and page["url"] == "results.jinja":
      engine.games[5].set_master()
    if page["url"] == "results.jinja"  and current_round_nb \
       or page["url"] == "Jeu 5" and page["phase"] == "reveal":
      engine.games[current_game_nb].logic()

    if refresh:
      engine.force_refresh()

  def refresh_monitoring(engine):
    if engine.admin_sid:
      engine.socketio.emit("refresh", None, room=engine.admin_sid)
  
  def force_refresh(engine):
    engine.socketio.emit("refresh", broadcast=True)

  def update_fields(engine, updates, players=None):
    socketio = engine.socketio
    if players:
      for player in players:
        if player.sid:
          player.emit("update_data", updates)
    else:
      socketio.emit("update_data", updates, broadcast=True)

  def log(engine, message):
    log_message = datetime.datetime.now().strftime("%H:%M:%S : ") + message
    engine.logger.info(log_message)
    engine.logs.append(log_message)


  def save_data(engine):
    socketio = engine.socketio
    engine.socketio = None
    with open("data.pck", "wb") as file:
      pickle.dump(engine, file)
    engine.socketio = socketio
    engine.refresh_monitoring()

  @staticmethod
  def load_data():
    with open("data.pck", "rb") as file:
      engine = pickle.load(file)
    engine.init_logger()
    engine.admin_sid = None
    for player in engine.players:
      player.sid = None
    return engine
