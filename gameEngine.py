import datetime
import pickle

from .players import Player
from .games import *
from .pages_ordering import pages

class gameEngine(object):
    pages = pages
    pages_by_round = { tuple(page['round']) : page for page in pages }
    def __init__(engine, socketio, players_raw):
        engine.socketio = socketio
        engine.admin_sid = None
        
        engine.logs = []
        
        engine.players = [Player(*player_raw) for player_raw in players_raw]
        for i, player in enumerate(engine.players):
            player.other_players = engine.players.copy()
            player.other_players.pop(i)
        
        engine.iterator = 0                  # pointeur pour indiquer sur quel page on est (fait réference a l'array 'pages')
        engine.waiting_count = 0             # Nombre de joueurs qui ont fait leur choix
        engine.game4_bonus = 0               # combien de fois les joueurs ont tous choisis des objets differents
        engine.masterPrizeBonus = False      # bonus pour le jeu 5
        engine.starMaster = None             # joueur ayant le plus d'étoiles à la fin du jeu 4
        engine.other_players = engine.players.copy() # Liste des autres joueurs pour le jeu 5
        engine.remaining_trials = 3
        engine.sabotage = False              # Sabotage du 3ème jeu si les participants sont trop coopératifs
        engine.questions = 0                 # Indique a quel question du quiz on est
        engine.frameId = 0
        engine.reveal = [False]*5


        
    
    def step(game):
        pass
    
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
        with open("data.pck", 'wb') as file:
            pickle.dump(engine, file)
        if engine.admin_sid:
            socketio.emit('refresh', None, room=engine.admin_sid)

    @staticmethod
    def load_data():
        with open("data.pck", 'rb') as file:
            engine = pickle.load(file)
        return engine

    def is_everyone_done(engine):
        return all(p.done for p in engine.players)

    def reveal_card(engine, card_id):
        if engine.reveal[card_id]: return
        engine.reveal[card_id] = True
        socketio = engine.socketio
        socketio.emit('reveal_card', card_id, broadcast=True)
        engine.save_data()

    def next_frame(engine):
        engine.frameId += 1
        socketio = engine.socketio
        socketio.emit('move_to_frame', engine.frameId, broadcast=True)
        engine.save_data()

    def previous_frame(engine):
        engine.frameId -= 1
        socketio = engine.socketio
        socketio.emit('move_to_frame', engine.frameId, broadcast=True)
        engine.save_data()

    def update_waiting_count(engine, count, total):
        updates = [("count", f"{count} / {total}")]
        waiting_players = (p  for p in engine.players if p["done"])
        engine.update_fields(updates, waiting_players)

