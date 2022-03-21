import random
import numpy as np
from abc import ABC, abstractmethod
from flask import Markup, flash

from .html_icon import icons


games_config = {
    "game1": {
        "background": "10.jpg", 
        "theme": ["#b65612","#dfaa84"], 
        "prizes": [200, 400, 600], 
        "stars": 1
    }, 
    "game2": {
        "background": "9.jpg", 
        "theme": ["#017e68","#6ecdbc"], 
        "prizes": [50, 100, 150], 
        "stars": 2
    }, 
    "game3": {
        "background": "8.jpg", 
        "theme": ["#3f6203","#a6ca68"], 
        "initial_flouze": 100, 
        "gains": [1.2, 1.5, 2], 
        "stars": 2
    }, 
    "game4": {
        "background": "6.jpg", 
        "theme": ["#024b66","#60a7c1"], 
        "prizes": [[[150, 100, 50, 0, "star"]], 
                   [[250, 150, 0, -150, "star"], 
                    [400, 250, 0, -250, "star"]], 
                   [[400, 200, -250, "star", "star"], 
                    [600, 250, -300, "star", "star"], 
                    [1000, 300, -400, "star", "star"]]], 
    }, 
    "game5": {
        "background": "7.jpg", 
        "theme": ["#6b017f","#c470d4"], 
        "prize": 2500, 
        "bonus": 500
    }
}

class Game(ABC):
    @abstractmethod
    def __init__(game, engine, game_id):
        game.engine = engine
        game.choices = [[None]*5 for _ in range(3)]
        game.is_done = [[False]*5 for _ in range(3)]
    
    def is_allowed_to_play(game, player):
        return 

    @abstractmethod
    def logic(game):
        pass
    
    @property
    def current_stage(game):
        return game.engine.current_stage
    
    @property
    def current_round_id(game):
        return game.current_stage[1] - 1
    
    def is_everyone_done(engine):
        return all(p.done for p in engine.players)

    def reveal_card(game, card_id):
        assert "reveal_states" in game.__dict__
        reveal_state = game.reveal_state[game.current_round_id]
        if reveal_state[card_id]: return
        reveal_state[card_id] = True
        socketio = game.engine.socketio
        socketio.emit('reveal_card', card_id, broadcast=True)
        game.engine.save_data()

    def next_frame(game):
        assert "frame_id" in game.__dict__
        game.frameId += 1
        socketio = game.engine.socketio
        socketio.emit('move_to_frame', game.frameId, broadcast=True)
        game.engine.save_data()

    def previous_frame(game):
        assert "frame_id" in game.__dict__
        game.frameId -= 1
        socketio = game.engine.socketio
        socketio.emit('move_to_frame', game.frameId, broadcast=True)
        game.engine.save_data()

    def update_waiting_count(game):
        is_done = game.is_done[game.current_round_id]
        waiting_players = [p 
            for p, is_done in zip(game.players, is_done) 
            if p["done"]
        ]
        total = 5 if game.game_id < 5 else 4
        updates = [("count", f"{len(waiting_players)} / {total}")]
        game.engine.update_fields(updates, waiting_players)

class Game1(Game):
    def __init__(game, engine):
        game.engine = engine
        game.game_id = 1
        game.config = games_config["game1"]
        game.frame_id = 0
    
    def logic(game):
        assert game.is_everyone_done()
        choices = game.choices[game.current_round_id]
        lottery = []
        for player, choice in zip(game.engine.players, choices):
            lottery += [player.ID] * choice
            player["message"] = Markup("Vous n'avez pas gagné la lotterie !"\
                                       + icons['sad'])
        if len(lottery) > 0:
            winner_id = random.choice(lottery)
            winner = game.engine.players[winner_id]
            prize = game.config["prizes"][game.current_round_id] 
            prize //= len(lottery)
            winner.flouze += prize
            winner.last_profit = prize
            
            game.engine.log(f"Le gagnant de la lotterie est {winner['name']} "\
                            f"qui a reçu {prize} Pièces")
            
            winner.message = Markup(
                f"Vous avez gagné la lotterie !<br>Vous avez reçu {prize} "\
                 + icons['coin'])
            
            if game.current_round_id == 3:
                won_stars = game.config["stars"]
                winner.stars += won_stars
                
                game.engine.log(f"{winner.name} a reçu {won_stars} étoile(s) "\
                                 "car iel a gagné la dernière manche")
                
                winner.message = Markup(
                    f"Vous avez gagné la lotterie !<br>Vous avez reçu "\
                    f"{prize} {icons['coin']}.<br>En plus vous recevez "\
                    f"{won_stars} {icons['star']} car vous avez remporté "\
                     "la dernière manche.")
                
        else:
            game.gameEngine.log("Il n'y a pas de gagnant à la lotterie "\
                                "car personne n'a participé.")

class Game2(Game):
    def __init__(game, engine):
        game.engine = engine
        game.game_id = 2
        game.config = games_config["game2"]
        game.reveal_state = [[False]*5 for _ in range(3)]

    def logic(game):
        assert game.is_everyone_done()
        for i in range(1, 6):
            count = 0 # nombre  de fois que i a été choisis
            player = None
            for p in game.engine.players:
                if p["choix"] == i:
                    count += 1
                    player = p # joueur gagnant
            if count == 1:
                prize = game.config["prize"]*i
                player["flouze"] += prize
                player['gain_a_partager'] = prize
                game.engine.log(player["name"] + " a remporté {prize} Pièces.")
                for p in game.engine.players:
                    p["message"] = Markup(f"{player['name']} a gagné et a remporté {prize} {icons['coin']}")
                if game.config['round'][1] == 3:
                    player["stars"] += game.config["stars"]
                    for player in game.engine.players:
                        player["message"] = Markup(f"{player['name']} a gagné et a remporté {icons['coin']}.<br>En plus iel recoit {game.config['stars']}  {icons['star']} car iel a remporté la dernière manche.")
                    game.engine.log(player["name"] + " a reçu " + str(game.config["stars"]) + " étoile(s) car iel a gagné la dernière manche")
                break
        else:
            game.engine.log("Personne n'a remporté de lot a cette manche")
            for p in game.engine.players: # initialiser les messages
                p["message"] = "Personne n'a remporté de lot a cette manche"

class Game3(Game):
    def __init__(game, engine):
        game.engine = engine
        game.game_id = 3
        game.config = games_config["game3"]
        
        # Sabotage du 3ème jeu si les participants sont trop coopératifs
        game.sabotage = False
    
    def start(game):
        sum = 0
        for player in game.engine.players:
            player.saved_flouze = max(0, player["flouze" ] - game.config['initial_flouze'])
            sum += player["saved_flouze"]
            player["flouze"] = game.config['initial_flouze']
        if sum > 1500:
            game.sabotage = True
        game.engine.log(f"L'argent des joueurs à été mis de coté. Ils leur restent tous {game.config['initial_flouze']} Pièces")

    def logic(game):
        assert game.is_everyone_done()
        pot_commun = 0
        pot_commun = sum(player.choice for player in game.engine.players)
        if game.sabotage:
            mises = [p['choix'] for p in game.engine.players]
            pot_commun = 1.2 * np.argmax(mises)
            game.engine.log("Cette manche a été sabotée car les participans on été trop coopératifs. Le contenu du pot commun avant l'ajout de la banque à été fixé à" + str(pot_commun))
        prize = int(pot_commun * game.config["gain"] // 5)
        game.engine.log(str(prize*5) + " Pièces ont été redistribué équitablement à tous les joueurs ce qui fait {prize} Pièces par joueur")
        for p in game.engine.players:
            p["flouze"] += prize
            p["message"] = Markup(f"Vous avez reçu {prize} {icons['coin']}")
        if game.config['round'][1] == 3:
            flouzes = [player['flouze'] for player in game.engine.players]
            winner_id = np.argmax(flouzes)
            winner = game.engine.players[winner_id]
            if flouzes.count(max(flouzes)) == 1:
                winner.stars += game.config["stars"]
                winner.message = Markup(f"Vous avez reçu {prize} {icons['coin']}.<br>En plus vous recevez {game.config['stars']} {icons['star']} car vous avez gagné le plus d'argent durant ce jeu.")
                game.engine.log(f"{winner.name} a reçu {game.config['stars']} étoile(s) car iel a gagné le plus d'argent durant ce jeu.")
            else:
                game.engine.log("Dû à une égalité aucune étoile n'a été distribuée")
    
    def end(game):
        for player in game.engine.players:
            player.flouze += player.saved_flouze
            player.saved_flouze = None
        game.engine.log("L'argent mis de coté à été remis en jeu")

class Game4(Game):
    def __init__(game, engine):
        game.engine = engine
        game.game_id = 4
        game.config = games_config["game4"]
        # combien de fois les joueurs ont tous choisis des objets differents
        game.bonuses = 0
        game.reveal_state = [[False]*5 for _ in range(3)]

    def logic(game):
        assert game.is_everyone_done()
        uniqueChoices = 0 # compte le nombre de choix uniques
        for p in game.engine.players:
            p['message'] = "Vous n'avez pas remporté le prix"
        for i in range(5):
            count = 0 # nombre de fois que le prix i a été choisis
            player = None
            for p in game.engine.players:
                if p["choix"] == i:
                    count += 1
                    player = p
            if count == 1:
                uniqueChoices += 1
                prize = game.config['prize'][game.bonuses][i]
                if prize == "star":
                    player["stars"] += 1
                    player["message"] = Markup("Vous avez remporté le prix : {icons['star']}")
                    game.engine.log(player["name"] + " a gagné une étoile")
                else:
                    player["flouze"] += prize
                    player['gain_a_partager'] = prize
                    player["message"] = Markup("Vous avez remporté le prix : {prize} {icons['coin']}")
                    game.engine.log(player["name"] + " a remporté {prize} Pièces")
        if uniqueChoices == 5:
            if pages[gameState['iterator']]['round'][1] == 3:
                gameState["masterPrizeBonus"] = True
                game.engine.log(f"Tous les joueurs ont choisis un prix différent donc le gros lot passe de {pages_by_round[(5, 0)]['prize']} à {pages_by_round[(5, 0)]['prize'] + pages_by_round[(5, 0)]['bonus']} Pièces")
            else:
                game.engine.log("Tous les joueurs ont choisis un prix différent donc un bonus s'applique pour la manche suivante")
                gameState["game4_bonus"] += 1

class Game5(Game):
    def __init__(game, engine, master, with_bonus):
        game.engine = engine
        game.game_id = 5
        game.config = games_config["game5"]
        # joueur ayant le plus d'étoiles à la fin du jeu 4
        game.master = master
        # reste des joueurs
        game.other_players = engine.players.copy()
        game.other_players.pop(master.ID)
        # bonus pour le jeu 5
        game.with_bonus = with_bonus
        game.remaining_trials = 3

    def start(game):
        for p in game.other_players:
            p['message'] = f"Veuillez attendre la nouvelle proposition de {game.master.name} ..."

        for i in range(3):
            op[i]['question'] = quiz[0][i]

    def logic(game):
        pass

    def end(game):
        gameState['iterator'] = len(pages) - 1
        for p in game.engine.players:
            p["done"] = False
        gameState['done'] = 0
        refresh_all_pages()

class Quiz(Game):
    def __init__(game, engine, master, bonus):
        game.engine = engine
        game.question_id = 0

    def logic(game):
        pass

def end_waiting():
    gameState['iterator'] += 1
    for p in game.engine.players:
        p["done"] = False
    gameState['done'] = 0
    refresh_all_pages()

def check_action_allowed(player, gameNb):
    if player["done"]: return render_template("en_attente.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], done=gameState['done'], user=player, players=players, background=pages[gameState['iterator']]['background'])
    if pages[gameState['iterator']]['round'][0] != gameNb: return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, page=pages[gameState['iterator']], gameState=gameState, background=pages[gameState['iterator']]['background'])
    return None

