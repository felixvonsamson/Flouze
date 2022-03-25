import random
import numpy as np
from abc import ABC, abstractmethod
from flask import Markup

from .html_icons import icons
from .pages_ordering import pages


games_config = {
  "game1": {
    "background": "10.jpg",
    "theme_colors": ["#b65612","#dfaa84"],
    "prizes": [200, 400, 600],
    "3rd_round_stars": 1
  },
  "game2": {
    "background": "9.jpg",
    "theme_colors": ["#017e68","#6ecdbc"],
    "prizes": [50, 100, 150],
    "3rd_round_stars": 2
  },
  "game3": {
    "background": "8.jpg",
    "theme_colors": ["#3f6203","#a6ca68"],
    "initial_flouze": 100,
    "interests": [1.2, 1.5, 2],
    "3rd_round_stars": 2
  },
  "game4": {
    "background": "6.jpg",
    "theme_colors": ["#024b66","#60a7c1"],
    "prizes": [[[150, 100, 50, 0, "star"]],
               [[250, 150, 0, -150, "star"],
                [400, 250, 0, -250, "star"]],
               [[400, 200, -250, "star", "star"],
                [600, 250, -300, "star", "star"],
                [1000, 300, -400, "star", "star"]]],
  },
  "game5": {
    "background": "7.jpg",
    "theme_colors": ["#6b017f","#c470d4"],
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
  def __init__(game, engine):
    game.engine = engine
    game.choices = [[None]*5 for _ in range(3)]
    game.is_done = [[False]*5 for _ in range(3)]
    game.frame_id = 0


  @abstractmethod
  def logic(game):
    pass

  @property
  def current_stage(game):
    return game.engine.current_stage

  @property
  def current_round_id(game):
    assert (game.current_stage[1] in [1, 2, 3])
    return game.current_stage[1] - 1

  @property
  def current_choices(game):
    return game.choices[game.current_round_id]

  @property
  def current_done(game):
    return game.is_done[game.current_round_id]

  @property
  def current_reveal_state(game):
    assert "reveal_states" in game.__dict__
    return game.reveal_states[game.current_round_id]

  @property
  def current_waiting_count(engine):
    return sum(engine.current_done)

  @property
  def is_everyone_done(game):
    return all(game.current_done)

  def is_allowed_to_play(game, player, game_nb):
    return game_nb == game.game_nb and not player.is_done

  def reveal_card(game, card_id):
    assert "reveal_states" in game.__dict__
    reveal_state = game.current_reveal_state
    if reveal_state[card_id]: return
    reveal_state[card_id] = True
    socketio = game.engine.socketio
    socketio.emit("reveal_card", card_id, broadcast=True)
    print(f"\n{card_id}\n")
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
    is_done = game.current_done
    waiting_players = [player
      for player, is_done in zip(game.engine.players, is_done)
      if is_done
    ]
    total = 5 if game.game_nb < 5 else 4
    updates = [("count", f"{len(waiting_players)} / {total}")]
    game.engine.update_fields(updates, waiting_players)


class Game1(Game):
  def __init__(game, engine):
    super().__init__(engine)
    game.engine = engine
    game.game_nb = 1
    game.config = games_config["game1"]
    

  def logic(game):
    assert game.is_everyone_done
    choices = game.current_choices
    lottery = []
    for player, nb_tickets in zip(game.engine.players, choices):
      lottery += [player.ID] * nb_tickets
      player.message = Markup(
        f"Vous n'avez pas gagné la lotterie ! {icons['sad']}")
    if len(lottery) > 0:
      winner_id = random.choice(lottery)
      winner = game.engine.players[winner_id]
      prize = game.config["prizes"][game.current_round_id]
      prize //= len(lottery)
      winner.flouze += prize
      winner.last_profit = prize

      game.engine.log(
        f"Le gagnant de la lotterie est {winner.name} "\
        f"qui a reçu {prize} Pièces.")

      winner.message = Markup(
        f"Vous avez gagné la lotterie !<br>Vous avez reçu {prize} "\
        f"{icons['coin']}")

      if game.current_round_id == 2:
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

  def end(game):
    game.engine.games[2] = Game2(game.engine)


class Game2(Game):
  def __init__(game, engine):
    super().__init__(engine)
    game.engine = engine
    game.game_nb = 2
    game.config = games_config["game2"]
    
    game.reveal_states = [[False]*5 for _ in range(3)]

  def logic(game):
    assert game.is_everyone_done
    choices = game.current_choices
    unique_choices, counts = np.unique(choices, return_counts=True)
    if 1 in counts:
      winning_value = unique_choices[counts.index(1)]
      for player, choice in zip(game.engine.players, choices):
        round_id = game.current_round_id
        if choice == winning_value:
          winner = player
          prize = game.config["prizes"][round_id] * choice
          player.flouze += prize
          player.last_profit = prize
          if round_id in [0, 1]:
            game.engine.log(
              f"{player.name} a remporté {prize} Pièces.")
          else:
            won_stars = game.config["3rd_round_stars"]
            player.stars += won_stars
            game.engine.log(
              f"{player.name} a reçu {won_stars} étoile(s) "\
               "car iel a gagné la dernière manche")
      if round_id in [0, 1]:
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

  def end(game):
    game.engine.games[3] = Game3(game.engine)


class Game3(Game):
  def __init__(game, engine):
    super().__init__(engine)
    game.engine = engine
    game.game_nb = 3
    game.config = games_config["game3"]
    
    game.done_stars = [False] * 5
    # Sabotage du 3ème jeu si les participants sont trop coopératifs
    game.sabotage = False
    game.start()

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
    assert game.is_everyone_done

    inputs = game.current_choices
    common_pot = sum(inputs)
    if game.sabotage:
      common_pot = 1.2 * np.max(common_pot)
      game.engine.log(
        f"Cette manche a été sabotée car les participans on été trop "\
         "coopératifs. Le contenu du pot commun avant l'ajout de la "\
        f"banque à été fixé à {common_pot}")

    interest = game.config["interests"][game.current_round_id]
    prize = int(common_pot * interest  // 5)
    game.engine.log(
      f"{5 * prize} Pièces ont été redistribué équitablement à "\
      f"tous les joueurs ce qui fait {prize} Pièces par joueur-")

    for player in game.engine.players:
      player.flouze += prize
      player.message = Markup(f"Vous avez reçu {prize} {icons['coin']}.")

    if game.current_round_id == 2:
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

    game.engine.games[4] = Game4(game.engine)


class Game4(Game):
  def __init__(game, engine):
    super().__init__(engine)
    game.engine = engine
    game.game_nb = 4
    game.config = games_config["game4"]
    # combien de fois les joueurs ont tous choisis des objets differents
    game.bonuses = [False] * 3
    game.reveal_states = [[False]*5 for _ in range(3)]

  @property
  def current_bonuses(game):
    round_id = game.current_round_id
    return sum(game.bonuses[:round_id])

  @property
  def current_bonus(game):
    round_id = game.current_round_id
    return game.bonuses[round_id]
  @current_bonus.setter
  def current_bonus(game, bonus):
    round_id = game.current_round_id
    game.bonuses[round_id] = bonus

  @property
  def current_prizes(game):
    return game.config['prize'][game.bonuses]
  
  def logic(game):
    assert game.is_everyone_done
    # compte le nombre de choix uniques
    choices = game.current_choices
    unique_choices = set(np.unique(choices))
    for player, choice in zip(game.engine.players, choices):
      if choice in unique_choices:
        prize = game.current_prizes[choice]
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
      if game.current_round_id in [0, 1]:
        game.engine.log(
          "Tous les joueurs ont choisis un prix différent "\
          "donc un bonus s'applique pour la manche suivante")
        game.current_bonus = True
      else:
        master_prize = games_config['game5']['prize']
        master_prize_with_bonus = games_config['game5']['prize'] \
                      + games_config['game5']['bonus']
        game.engine.log(
          f"Tous les joueurs ont choisis un prix différent "\
          f"donc le gros lot passe de {master_prize} "\
          f"à {master_prize_with_bonus} Pièces.")

  def end(game):
    stars = [player.stars for player in game.engine.players]
    game.engine.log(
       "Le nombre d'etoiles pour chaque joueur est "\
      f"respectivement : {stars}")
    if stars.count(max(stars)) == 1:
      master_id = np.argmax(stars)
      master = game.engine.players[master_id]
      prize = games_config["game5"]["prize"] + \
          (game.current_bonuses == 3) * games_config["game5"]["bonus"]
      master.flouze += prize
      game.engine.log(
        f"{master.name} a le plus d'étoiles et remporte ainsi "\
        f"la somme de {prize} pièces pour le cinquième jeu.")
      game.engine.games[5] = Game5(game.engine, master)
      for player in game.engine.games[5].other_players:
        player.message = Markup(
          f"{master.name} a le plus d'étoiles et est ainsi "\
          f"en possesion de la somme de {prize} {icons['coin']}."\
           "pour le 5ème jeu")
      master.message = Markup(
         "Vous avez le plus d'étoiles et êtes ainsi en possesion de "\
        f"la somme de {prize} {icons['coin']} pour le 5ème jeu.")

    else:
      game.engine.log(
        "Dû à une égalité en terme d'étoiles, personne ne remporte "\
        "le gros lot et le cinquième jeu est annulé")
      for player in game.engine.players:
        player.message = "Dû à une égalité en terme d'étoiles, "\
                         "personne ne remporte le gros lot"\
                         "et le cinquième jeu est annulé"


class Game5(Game):
  def __init__(game, engine, master, with_bonus):
    super().__init__(engine)
    game.engine = engine
    game.game_nb = 5
    game.config = games_config["game5"]
    # joueur ayant le plus d'étoiles à la fin du jeu 4
    game.master = master
    # reste des joueurs
    game.other_players = engine.players.copy()
    game.other_players.pop(master.ID)
    game.propositions = [[0]*5 for _ in range(3)]
    game.question_id = -1

  @property
  def current_proposition(game):
    round_id = game.current_round_id
    return game.propositions[round_id]
  @property
  def current_proposition(game, proposition):
    round_id = game.current_round_id
    game.propositions[round_id] = proposition

  @property
  def current_guesser(game):
    return game.other_players[game.question_id]

  def start_round(game):
    for players in game.other_players:
      players.message = f"Veuillez attendre la nouvelle proposition "\
                f"de {game.master.name} ..."
    game.next_question()

  def next_question(game):
    game.question_id += 1
    guessers = game.other_players.copy()
    guessers.pop(game.question_id)
    for player, question in zip(guessers, quiz[game.question_id]):
      player.question = question


  def logic(game):
    if sum(game.current_choices) >= 3:
      game.master.message = Markup(
        f"Votre proposition a été acceptée par la majorité.<br>Vous repartez "\
        f"donc avec {game.master.flouze} {icons['coin']} ce qui correspond "\
        f"à {game.master.flouze / 10} €.")
      for i, player in enumerate(game.other_players):
        offer = game.current_proposition[i]
        game.master.flouze -= offer
        player.flouze += offer
        player.message = Markup(
            f"La proposition à été acceptée par la majorité des joueurs.<br>"\
            f"Vous avez recu {offer} {icons['coin']} de {game.master.name}."\
            f"<br>Vous repartez donc avec {player.flouze} {icons['coin']} "\
            f"ce qui correspond à {player.flouze / 10} €.")
      game.end()
    else:
      if game.current_round_id == 2:
        prize = games_config["game5"]["prize"] + \
            (game.bonuses == 3) * games_config["game5"]["bonus"]
        game.master.flouze -= prize
        game.master.message = Markup(
          f"Votre dernière proposition a été refusée par "\
          f"la majorité. Les {prize} vous sont donc retirés.")
        for player in game.other_players:
          player.message = Markup(
            f"Auccun accord à été trouvé apprès ces 3 essais donc "\
            f"{game.master.name} ne remporte pas les "\
            f"{prize} {icons['coin']}.")
        game.end()
      else:
        game.master.message = "Votre proposition a été refusée "\
                    "par la majorité !"
        for player in game.other_players:
          player.message = Markup(
            "La proposition à été refusée par au moins 2 joueurs."\
            "<br>En attente d'une nouvelle proposition...")
        game.engine.next_page()

  def end(game):
    game.engine.iterator = len(pages) - 1
    game.engine.refresh_all_pages()

