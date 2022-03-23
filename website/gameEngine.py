import datetime
import pickle

from .players import Player
from .games import Game1, Game2, Game3, Game4, Game5
from .pages_ordering import pages

class gameEngine(object):
  pages = pages

  def __init__(engine, players_raw):
    engine.socketio = None
    engine.admin_sid = None

    engine.logs = []

    engine.players = [Player(*player_raw, engine)
              for player_raw in players_raw]
    for i, player in enumerate(engine.players):
      player.other_players = engine.players.copy()
      player.other_players.pop(i)
    engine.players_by_name = { p.name: p for p in engine.players }

    engine.games = {
      1: Game1(engine),
      2: None,
      3: None,
      4: None,
      5: None
    }

    # pointeur pour indiquer sur quelle page on est (l'array 'pages')
    engine.iterator = 0

    engine.log("LE JEU A COMMENCÉ !")

  @property
  def current_page(engine):
    return gameEngine.pages[engine.iterator]

  @property
  def current_stage(engine):
    return gameEngine.pages[engine.iterator]["stage"]

  @property
  def current_game(engine):
    assert (engine.current_stage[0] in [1, 2, 3, 4, 5])
    return engine.games[engine.current_stage[0]]


  def next_page(engine):
    engine.iterator += 1
    stage = engine.current_stage
    engine.log(
      f"Passage à la page suivante : {engine.current_page['url']} "\
      f"(jeu {stage[0]}, manche {stage[1]})")

    current_game_nb, current_round_nb = engine.current_stage
    if current_game_nb > 1 and current_round_nb == 0:
      engine.games[current_game_nb - 1].end()

    if engine.current_page["url"] == "results.html":
      engine.games[current_game_nb].logic()

    engine.force_refresh()

  def refresh_monitoring(engine):
    if engine.admin_sid:
      engine.socketio.emit('refresh', None, room=engine.admin_sid)
  
  def force_refresh(engine):
    engine.socketio.emit('refresh', None, broadcast=True)

  def update_fields(engine, updates, players=None):
    socketio = engine.socketio
    if players:
      for player in players:
        if player.sid:
          socketio.emit('update_data', updates, room=player.sid)
    else:
      socketio.emit('update_data', updates, broadcast=True)

  def log(engine, message):
    log_message = datetime.datetime.now().strftime('%H:%M:%S : ') + message
    engine.logs.append(log_message)


  def save_data(engine):
    socketio = engine.socketio
    engine.socketio = None
    with open("data.pck", 'wb') as file:
      pickle.dump(engine, file)
    engine.socketio = socketio
    if engine.admin_sid:
      socketio.emit('refresh', None, room=engine.admin_sid)

  @staticmethod
  def load_data():
    with open("data.pck", 'rb') as file:
      engine = pickle.load(file)
    engine.admin_sid = None
    for player in engine.players:
      player.sid = None
    return engine
