import datetime
import pickle
from flask import Markup, flash

from .players import Player
from .games import Game1, Game2, Game3, Game4, Game5
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
        
        engine.games = [Game1(engine), 
                        Game2(engine), 
                        Game3(engine), 
                        Game4(engine), 
                        Game5(engine)]

        # pointeur pour indiquer sur quelle page on est (l'array 'pages')
        engine.iterator = 0

    @property
    def current_page(engine):
        return gameEngine.pages[engine.iterator]

    @property
    def current_stage(engine):
        return gameEngine.pages[engine.iterator]["stage"]
    
    @property
    def current_game(engine):
        return engine.games[engine.current_stage[0]]
    
    @property
    def current_waiting_count(engine):
        if engine.current_stage[1] not in [1, 2, 3]:
            return None
        round_id = engine.current_stage[1] - 1
        return sum(engine.current_game.is_done[round_id])
    
    @property
    def current_presentation_frame(engine):
        if engine.current_stage not in [(1, 0)]:
            return None
        return engine.current_game.current_frame_id
    
    def step(engine):
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


