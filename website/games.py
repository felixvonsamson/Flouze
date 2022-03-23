import random
import numpy as np
from abc import ABC, abstractmethod
from flask import Markup, flash

from .html_icons import icons
from .pages_ordering import pages


games_config = {
    "game1": {
        "background": "10.jpg", 
        "theme": ["#b65612","#dfaa84"], 
        "prizes": [200, 400, 600], 
        "3rd_round_stars": 1
    }, 
    "game2": {
        "background": "9.jpg", 
        "theme": ["#017e68","#6ecdbc"], 
        "prizes": [50, 100, 150], 
        "3rd_round_stars": 2
    }, 
    "game3": {
        "background": "8.jpg", 
        "theme": ["#3f6203","#a6ca68"], 
        "initial_flouze": 100, 
        "interests": [1.2, 1.5, 2], 
        "3rd_round_stars": 2
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


quiz = [
    ["_______ _______ _ a-t-il __ __ drapeau ______ ?", 
    "_______ d’étoiles _ ____ sur __ ______ valaisan ?", 
    "Combien _______ y ____ __ le _______ ______ ?"], 
    ["Quel ____ __ enclavé ____ le _______ ?", 
    "___ pays ___ ______ dans __ _______ ?", 
    "___ ____ est ______ ____ __ Sénégal ?"], 
    ["Combien _ ___ de _____ __ tram _ ________ ?", 
    "_______ y ___ __ lignes __ ____ à ________ ?", 
    "_______ _ a-t-il __ ____ de ____ _ Bordeaux ?"], 
    ["Quel ____ ___ pseudo ___ ____ of ____ ?", 
    "____ était ___ ______ sur ____ __ clans ?", 
    "____ ____ mon _____ ___ clash __ ____ ?"], 
    ["Comment _______ __ parc ______ _ l’université __ _______ ?", 
    "________ s’appelle __ ___ adjacent _ ________ de _______ ?", 
    "________ _______ le ____ ______ à _________ __ Montréal ?"]
]


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
    def current_round(game):
        return game.current_stage[1] - 1
    
    @property
    def current_choice(game):
        return game.choices[game.current_round]
    
    @property
    def current_done(game):
        return game.is_done[game.current_round]
    
    def check_action_allowed(game, player, game_id):
        return game_id == game.game_id and not player.is_done

    def is_everyone_done(game):
        return all(game.is_done[game.current_round])

    def reveal_card(game, card_id):
        assert "reveal_states" in game.__dict__
        reveal_state = game.reveal_state[game.current_round]
        if reveal_state[card_id]: return
        reveal_state[card_id] = True
        socketio = game.engine.socketio
        socketio.emit("reveal_card", card_id, broadcast=True)
        game.engine.save_data()

    def next_frame(game):
        assert "frame_id" in game.__dict__
        game.frame_id += 1
        socketio = game.engine.socketio
        socketio.emit("move_to_frame", game.frame_id, broadcast=True)
        game.engine.save_data()

    def previous_frame(game):
        assert "frame_id" in game.__dict__
        game.frame_id -= 1
        socketio = game.engine.socketio
        socketio.emit("move_to_frame", game.frame_id, broadcast=True)
        game.engine.save_data()

    def update_waiting_count(game):
        is_done = game.is_done[game.current_round]
        waiting_players = [player
            for player, is_done in zip(game.players, is_done) 
            if is_done
        ]
        total = 5 if game.game_id < 5 else 4
        updates = [("count", f"{len(waiting_players)} / {total}")]
        game.engine.update_fields(updates, waiting_players)
    
    def end_waiting(game):
        game.engine.iterator += 1
        game.engine.refresh_all_pages()


class Game1(Game):
    def __init__(game, engine):
        game.engine = engine
        game.game_id = 1
        game.config = games_config["game1"]
        game.frame_id = 0
        game.choices = [[None]*5 for _ in range(3)]
        game.is_done = [[False]*5 for _ in range(3)]
    
    def logic(game):
        assert game.is_everyone_done()
        choices = game.choices[game.current_round]
        lottery = []
        for player, nb_tickets in zip(game.engine.players, choices):
            lottery += [player.ID] * nb_tickets
            player.message = Markup(
                f"Vous n'avez pas gagné la lotterie ! {icons['sad']}")
        if len(lottery) > 0:
            winner_id = random.choice(lottery)
            winner = game.engine.players[winner_id]
            prize = game.config["prizes"][game.current_round] 
            prize //= len(lottery)
            winner.flouze += prize
            winner.last_profit = prize
            
            game.engine.log(
                f"Le gagnant de la lotterie est {winner['name']} "\
                f"qui a reçu {prize} Pièces.")
            
            winner.message = Markup(
                f"Vous avez gagné la lotterie !<br>Vous avez reçu {prize} "\
                f"{icons['coin']}")
            
            if game.current_round == 3:
                won_stars = game.config["3rd_round_stars"]
                winner.stars += won_stars
                
                game.engine.log(
                    f"{winner.name} a reçu {won_stars} étoile(s) "\
                     "car iel a gagné la dernière manche")
                
                winner.message = Markup(
                    f"Vous avez gagné la lotterie !<br>Vous avez reçu "\
                    f"{prize} {icons['coin']}.<br>En plus vous recevez "\
                    f"{won_stars} {icons['star']} car vous avez remporté "\
                     "la dernière manche.")
                
        else:
            game.gameEngine.log(
                "Il n'y a pas de gagnant à la lotterie "\
                "car personne n'a participé.")


class Game2(Game):
    def __init__(game, engine):
        game.engine = engine
        game.game_id = 2
        game.config = games_config["game2"]
        game.choices = [[None]*5 for _ in range(3)]
        game.is_done = [[False]*5 for _ in range(3)]
        game.reveal_state = [[False]*5 for _ in range(3)]

    def logic(game):
        assert game.is_everyone_done()
        choices = game.choices[game.current_round]
        unique_choices = np.unique(choices)
        if unique_choices:
            winning_value = np.min(unique_choices)
            for player, choice in zip(game.engine.players, choices):
                if choice == winning_value:
                    winner = player
                    prize = game.config["prize"] * choice
                    player.flouze += prize
                    player.last_profit = prize
                    if game.config['round'][1] in [0, 1]:
                        game.engine.log(
                            f"{player.name} a remporté {prize} Pièces.")
                    else:
                        won_stars = game.config["3rd_round_stars"]
                        player.stars += won_stars
                        game.engine.log(
                            f"{player.name} a reçu {won_stars} étoile(s) "\
                             "car iel a gagné la dernière manche")
            if game.config['round'][1] in [0, 1]:
                for player in game.engine.players:
                    player.message = Markup(
                        f"{winner.name} a gagné et a remporté "\
                        f"{prize} {icons['coin']}")
            else:
                for player in game.engine.players:
                    won_stars = game.config["stars"]
                    player.message = Markup(
                        f"{player.name} a gagné et a remporté {icons['coin']}."\
                        f"<br>En plus iel recoit {won_stars} {icons['star']} "\
                         "car iel a remporté la dernière manche.")
        else:
            game.engine.log("Personne n'a remporté de lot a cette manche.")
            for player in game.engine.players:
                player.message = "Personne n'a remporté de lot a cette manche."


class Game3(Game):
    def __init__(game, engine):
        game.engine = engine
        game.game_id = 3
        game.config = games_config["game3"]
        
        # Sabotage du 3ème jeu si les participants sont trop coopératifs
        game.sabotage = False
    
    def start(game):
        total_saved = 0
        initial_flouze = game.config["initial_flouze"]
        for player in game.engine.players:
            player.saved_flouze = max(0, player.flouze - initial_flouze)
            total_saved += player.saved_flouze
            player.flouze = game.config['initial_flouze']
        if total_saved > 1500:
            game.sabotage = True
        game.engine.log(
             "L'argent des joueurs à été mis de coté. "\
            f"Ils leur restent tous {initial_flouze} Pièces")

    def logic(game):
        assert game.is_everyone_done()
        
        inputs = game.choices[game.current_round]
        common_pot = sum(inputs)
        if game.sabotage:
            common_pot = 1.2 * np.argmax(common_pot)
            game.engine.log(
                f"Cette manche a été sabotée car les participans on été trop "\
                 "coopératifs. Le contenu du pot commun avant l'ajout de la "\
                f"banque à été fixé à {common_pot}")
        
        interest = game.config["interests"][game.current_round]
        prize = int(common_pot * interest  // 5)
        game.engine.log(
            f"{5 * prize} Pièces ont été redistribué équitablement à "\
            f"tous les joueurs ce qui fait {prize} Pièces par joueur-")
        
        for player in game.engine.players:
            player.flouze += prize
            player.message = Markup(f"Vous avez reçu {prize} {icons['coin']}.")
        
        if game.current_round == 2:
            flouzes = [player.flouze for player in game.engine.players]
            winner_id = np.argmax(flouzes)
            winner = game.engine.players[winner_id]
            if flouzes.count(max(flouzes)) == 1:
                won_stars = game.config["3rd_round_stars"]
                winner.stars += won_stars
                game.engine.log(
                    f"{winner.name} a reçu {won_stars} étoile(s) car "\
                     "iel a gagné le plus d'argent durant ce jeu.")
                winner.message = Markup(
                    f"Vous avez reçu {prize} {icons['coin']}.<br>En plus "\
                    f"vous recevez {won_stars} {icons['star']} "\
                    "car vous avez gagné le plus d'argent durant ce jeu.")
            else:
                game.engine.log(
                    "Dû à une égalité aucune étoile n'a été distribuée")
    
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
        # compte le nombre de choix uniques
        choices = game.choices[game.current_round]
        unique_choices = set(np.unique(choices))
        for player, choice in zip(game.engine.players, choices):
            if choice in unique_choices:
                prize = game.config['prize'][game.bonuses][choice]
                if prize == "star":
                    player.stars += 1
                    game.engine.log(f"{player.name} a gagné une étoile.")
                    player.message = Markup(
                        f"Vous avez remporté le prix {icons['star']}")
                else:
                    player.flouze += prize
                    player.last_profit = prize
                    game.engine.log(f"{player.name} a remporté {prize} Pièces.")
                    player.message = Markup(
                        f"Vous avez remporté le prix {prize} {icons['coin']}.")
            else:
                player.message = "Vous n'avez pas remporté le prix."
        
        if len(unique_choices) == 5:
            if game.current_round in [0, 1]:
                game.engine.log(
                    "Tous les joueurs ont choisis un prix différent "\
                    "donc un bonus s'applique pour la manche suivante")
                game.bonuses += 1
            else:
                master_prize = games_config['game5']['prize']
                master_prize_with_bonus = games_config['game5']['prize'] \
                                          + games_config['game5']['bonus']
                game.engine.log(
                    f"Tous les joueurs ont choisis un prix différent "\
                    f"donc le gros lot passe de {master_prize} "\
                    f"à {master_prize_with_bonus} Pièces.")
                

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
        for players in game.other_players:
            players.message = f"Veuillez attendre la nouvelle proposition "\
                               "de {game.master.name} ..."

        guessers = game.other_players.copy()
        guessers.pop(0)
        for player, question in zip(guessers, quiz[0]):
            player.question = question
    
    def logic(game):
        pass

    def end(game):
        game.engine.iterator = len(pages) - 1
        game.engine.refresh_all_pages()

class Quiz(Game):
    def __init__(game, engine, master, bonus):
        game.engine = engine
        game.question_id = 0

    def logic(game):
        pass

