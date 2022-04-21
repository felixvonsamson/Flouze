import random
import numpy as np
from abc import ABC, abstractmethod
from flask import Markup

from .html_icons import icons
from .pages_ordering import pages

colors = [
  { "id": 0, "name": "bleu" }, 
  { "id": 1, "name": "rouge" }, 
  { "id": 2, "name": "jaune" }, 
  { "id": 3, "name": "vert" }, 
  { "id": 4, "name": "violet" }
]

games_config = {
  "colors": {
    "background": "2.jpg", 
  }, 
  "game1": {
    "title": "La loterie", 
    "background": "10.jpg", 
    "prizes": [200, 400, 600], 
    "3rd_round_stars": 1
  }, 
  "game2": {
    "title": "L'enchère inversée", 
    "background": "9.jpg", 
    "prizes": [50, 100, 150], 
    "3rd_round_stars": 2
  }, 
  "game3": {
    "title": "Le pot commun", 
    "background": "8.jpg", 
    "initial_flouze": 100, 
    "interests": [1.2, 1.5, 2], 
    "3rd_round_stars": 2
  }, 
  "game4": {
    "title": "Le con promis", 
    "background": "6.jpg", 
    "prizes": [[[150, 100, 50, 0, "star"]], 
               [[350, 150, 0, -50, "star"], 
                [500, 200, 0, -100, "star"]], 
               [[500, 250, -150, "star", "star"], 
                [700, 300, -250, "star", "star"], 
                [900, 400, -400, "star", "star"]]]
  }, 
  "game5": {
    "title": "Le bras de fer", 
    "background": "7.jpg",
    "prize": 3000,
    "bonus": 500,
    "quiz_prize": 30
  }
}


quiz = [
  (["_______ _______ _ a-t-il __ __ drapeau ______ ?", 
  "_______ d’étoiles _ ____ sur __ ______ valaisan ?", 
  "Combien _______ y ____ __ le _______ ______ ?"], 
  ["Combien d'étoiles y a-t-il sur le drapeau valaisan ?", 
  "13"]), 
  (["Quel ____ __ enclavé ____ le _______ ?", 
  "___ pays ___ ______ dans __ _______ ?", 
  "___ ____ est ______ ____ __ Sénégal ?"], 
  ["Quel pays est enclavé dans le Sénégal ?", 
  "La Gambie"]), 
  (["Combien _ ___ de _____ __ tram _ ________ ?", 
  "_______ y ___ __ lignes __ ____ à ________ ?", 
  "_______ _ a-t-il __ ____ de ____ _ Bordeaux ?"], 
  ["Combien y a-t-il de lignes de tram à Bordeaux ?", 
  "4"]), 
  (["Quel ____ ___ pseudo ___ ____ of ____ ?", 
  "____ était ___ ______ sur ____ __ clans ?", 
  "____ ____ mon _____ ___ clash __ ____ ?"], 
  ["Quel était mon pseudo sur clash of clans ?", 
  "FvS"]), 
  (["Comment _______ __ parc ______ _ l’université __ _______ ?", 
  "________ s’appelle __ ___ adjacent _ ________ de _______ ?", 
  "________ _______ le ____ ______ à _________ __ Montréal ?"], 
  ["Comment s'appelle le parc adjacent à l'université de Montréal ?", 
  "Le parc du Mont-Royal"])
]


class Game(ABC):
  @abstractmethod
  def __init__(game, engine):
    game.engine = engine
    game.players = engine.players
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
    if game.current_stage[1] in [1, 2, 3]:
      return game.is_done[game.current_round_id]
    if game.engine.current_page["url"] == "choix_etoiles.jinja":
      return game.is_done_stars
    return None

  @property
  def current_reveal_state(game):
    assert "reveal_states" in game.__dict__
    return game.reveal_states[game.current_round_id]

  @property
  def current_waiting_count(game):
    return sum(game.current_done)

  @property
  def is_everyone_done(game):
    return all(game.current_done)

  def is_allowed_to_play(game, player, game_nb):
    return game_nb == game.game_nb \
           and game.current_round_id in [0, 1, 2] \
           and not player.is_done

  def reveal_card(game, card_id):
    assert "reveal_states" in game.__dict__
    reveal_state = game.current_reveal_state
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
    is_done = game.current_done
    waiting_players = [player
      for player, is_done in zip(game.players, is_done)
      if is_done
    ]
    if game.engine.current_page["url"] != "Jeu 5": 
      updates = [("count", f"{len(waiting_players)} / 5")]
    else:
      updates = [("count", f"{len(waiting_players) - 1} / 4")]
    game.engine.update_fields(updates, waiting_players)

class Colors(Game):
  def __init__(game, engine):
    game.engine = engine
    game.game_nb = 0
    game.config = games_config["colors"]
    game.colors = colors
    game.owner = [None]*5
    game.choices = [[None]*5]
    game.is_done = [[False]*5]
  
  def set_choice(game, player, color_id):
    updates = []
    last_choice  = game.choices[0][player.ID]
    if last_choice != None :
      game.owner[last_choice] = None
      updates.append((game.colors[last_choice]["name"], ""))
    game.owner[color_id] = player
    game.choices[0][player.ID] = color_id
    updates.append((game.colors[color_id]["name"], player.name))
    game.engine.update_fields(updates)
    player.is_done = True
  
  def logic(game):
    pass

  def end(game):
    for player in game.players:
      color_id = game.choices[0][player.ID]
      player.color = game.colors[color_id]
      game.engine.log(f"{player.name} a choisi la couleur "\
                      f"{player.color['name']}.")
      player.send_message("Vous avez choisi la couleur "\
                          f"{player.color['name']}.", emit=False)
  

class Game1(Game):
  def __init__(game, engine):
    super().__init__(engine)
    game.game_nb = 1
    game.config = games_config["game1"]
  
  def set_choice(game, player, tickets):
    game.current_choices[player.ID] = tickets
    game.engine.log(f"{player.name} a choisi {tickets} ticket(s).")
    player.flash_message(f"Vous avez choisi {tickets} ticket(s).")
    player.is_done = True
  
  def logic(game):
    assert game.is_everyone_done
    choices = game.current_choices
    lottery = []
    for player, nb_tickets in zip(game.players, choices):
      lottery += [player] * nb_tickets
      player.message = f"Vous n'avez pas gagné la loterie ! {icons['sad']}"
    if len(lottery) > 0:
      winner = random.choice(lottery)
      prize = game.config["prizes"][game.current_round_id]
      prize //= len(lottery)
      winner.flouze += prize
      winner.last_profit = prize
      game.engine.log(
        f"Le gagnant de la loterie est {winner.name} "\
        f"qui a reçu {prize} Pièces.")
      winner.message = \
        f"Vous avez gagné la loterie !<br>Vous avez reçu {prize} "\
        f"{icons['coin']} !"
      if game.current_round_id == 2:
        won_stars = game.config["3rd_round_stars"]
        winner.stars += won_stars
        game.engine.log(
          f"{winner.name} a reçu {won_stars} étoile(s) "\
           "car iel a gagné la dernière manche.")
        winner.message += Markup(
          f"<br>En plus vous recevez {won_stars} {icons['star']} "\
           "car vous avez remporté la dernière manche.")
    else:
      game.engine.log(
        "Il n'y a pas de gagnant à la loterie car personne n'a participé.")


class Game2(Game):
  def __init__(game, engine):
    super().__init__(engine)
    game.game_nb = 2
    game.config = games_config["game2"]
    game.reveal_states = [[False]*5 for _ in range(3)]
    game.permutations = [np.random.permutation(5) for _ in range(3)]
  
  @property
  def current_permutation(game):
    return game.permutations[game.current_round_id]
  
  def set_choice(game, player, number):
    game.current_choices[player.ID] = number
    game.engine.log(f"{player.name} a choisi le nombre {number}.")
    player.flash_message(f"Vous avez choisi le nombre {number}.")
    player.is_done = True
  
  def logic(game):
    assert game.is_everyone_done
    choices = game.current_choices
    values, counts = np.unique(choices, return_counts=True)
    if 1 in counts:
      winning_value = values[list(counts).index(1)]
      winner_id = choices.index(winning_value)
      winner = game.players[winner_id]
      round_id = game.current_round_id
      prize = game.config["prizes"][round_id] * int(winning_value)
      winner.flouze += prize
      winner.last_profit = prize
      game.engine.log(
        f"{winner.name} a remporté {prize} Pièces.")
      winner.message = f"Vous avez gagné et remportez {prize} {icons['coin']}."
      for player in winner.other_players:
        player.message = \
          f"{winner.name} a gagné et remporte {prize} {icons['coin']}."
      if round_id == 2:
        won_stars = game.config["3rd_round_stars"]
        winner.stars += won_stars
        game.engine.log(
          f"{winner.name} a reçu {won_stars} étoile(s) "\
          "car iel a gagné la dernière manche.")
        winner.message += Markup(
          f"<br>En plus vous recevez {won_stars} {icons['star']} "\
           "car vous avez remporté la dernière manche.")
        for player in winner.other_players:
          player.message += Markup(
            f"<br>En plus iel recoit {won_stars} {icons['star']} "\
             "car iel a remporté la dernière manche.")
    else:
      game.engine.log("Personne n'a remporté de lot à cette manche.")
      for player in game.players:
        player.message = "Personne n'a remporté de lot à cette manche."


class Game3(Game):
  def __init__(game, engine):
    super().__init__(engine)
    game.game_nb = 3
    game.config = games_config["game3"]
    game.real_gain = [0]*5
    # Sabotage du 3ème jeu si les participants sont trop coopératifs
    game.sabotage = False

  def start(game):
    total_saved = 0
    initial_flouze = game.config["initial_flouze"]
    for player in game.players:
      player.saved_flouze = max(0, player.flouze - initial_flouze)
      total_saved += player.saved_flouze
      player.flouze = game.config["initial_flouze"]
    if total_saved > 1500:
      game.sabotage = True
    game.engine.log(
       "L'argent des joueurs à été mis de coté. "\
      f"Ils leur restent tous {initial_flouze} Pièces")
  
  def set_choice(game, player, amount):
    player.flouze -= amount
    game.current_choices[player.ID] = amount
    game.engine.log(f"{player.name} a versé {amount} Pièces dans le pot commun")
    player.flash_message(
      f"Vous avez versé {amount} {icons['coin']} dans le pot commun")
    player.is_done = True
  
  def logic(game):
    assert game.is_everyone_done

    inputs = game.current_choices
    common_pot = sum(inputs)
    if game.sabotage:
      common_pot = int(1.2 * np.max(inputs))
      game.engine.log(
         "Cette manche a été sabotée car les participans ont été trop "\
         "coopératifs. Le contenu du pot commun avant l'ajout de la "\
        f"banque à été fixé à {common_pot}")
      game.sabotage = False

    interest = game.config["interests"][game.current_round_id]
    prize = int(common_pot * interest  // 5)
    game.engine.log(
      f"{5 * prize} Pièces ont été redistribuées équitablement à "\
      f"tous les joueurs ce qui fait {prize} Pièces par joueur.")

    for player, shared in zip(game.players, game.current_choices):
      player.flouze += prize
      game.real_gain[player.ID] += prize - shared
      player.message = f"Vous avez reçu {prize} {icons['coin']}."

    if game.current_round_id == 2:
      winner_id = np.argmax(game.real_gain)
      winner = game.players[winner_id]
      print(game.real_gain)
      if game.real_gain.count(max(game.real_gain)) == 1:
        won_stars = game.config["3rd_round_stars"]
        winner.stars += won_stars
        game.engine.log(
          f"{winner.name} a reçu {won_stars} étoile(s) car "\
           "iel a gagné le plus d'argent durant ce jeu.")
        winner.message = \
          f"Vous avez reçu {prize} {icons['coin']}.<br>En plus "\
          f"vous recevez {won_stars} {icons['star']} "\
          "car vous avez gagné le plus d'argent durant ce jeu."
      else:
        game.engine.log(
          "Dû à une égalité, aucune étoile n'a été distribuée")

  def end(game):
    for player in game.players:
      player.flouze += player.saved_flouze
      player.saved_flouze = 0
    game.engine.log("L'argent mis de coté a été remis en jeu")


class Game4(Game):
  def __init__(game, engine):
    super().__init__(engine)
    game.game_nb = 4
    game.config = games_config["game4"]
    # combien de fois les joueurs ont tous choisi des objets differents
    game.bonuses = [False] * 3
    game.reveal_states = [[False]*5 for _ in range(3)]

  @property
  def current_bonuses(game):
    assert game == game.engine.current_game
    return sum(game.bonuses[:game.current_round_id])
  @property
  def total_bonuses(game):
    return sum(game.bonuses)

  @property
  def current_bonus(game):
    return game.bonuses[game.current_round_id]
  @current_bonus.setter
  def current_bonus(game, bonus):
    game.bonuses[game.current_round_id] = bonus

  @property
  def current_prizes(game):
    return game.config["prizes"][game.current_round_id][game.current_bonuses]
  
  def set_choice(game, player, prize_id):
    game.current_choices[player.ID] = prize_id
    prizes = game.current_prizes
    prize = prizes[prize_id]
    if prize == "star":
      if player.choice == 3 :
        game.engine.log(f"{player.name} a choisi la deuxième étoile.")
      else :
        game.engine.log(f"{player.name} a choisi l'étoile.")
      player.flash_message(f"Vous avez choisi le prix : {icons['star']}")
    else:
      game.engine.log(f"{player.name} a choisi le prix : {prize} Pièces")
      player.flash_message(
        f"Vous avez choisi le prix : {prize} {icons['coin']}")
    player.is_done = True
  
  def logic(game):
    assert game.is_everyone_done
    # compte le nombre de choix uniques
    choices = game.current_choices
    values, count = np.unique(choices, return_counts=True)
    unique_choices = set(values[np.where(count == 1)])
    for player, choice in zip(game.players, choices):
      if choice in unique_choices:
        prize = game.current_prizes[choice]
        if prize == "star":
          player.stars += 1
          game.engine.log(f"{player.name} a gagné une étoile.")
          player.message = f"Vous avez remporté le prix {icons['star']}"
        else:
          player.flouze += prize
          player.last_profit = prize
          game.engine.log(f"{player.name} a remporté {prize} Pièces.")
          player.message = \
            f"Vous avez remporté le prix {prize} {icons['coin']}."
      else:
        player.message = "Vous n'avez pas remporté le prix."

    if len(unique_choices) == 5:
      if game.current_round_id in [0, 1]:
        game.engine.log(
          "Tous les joueurs ont choisi un prix différent "\
          "donc un bonus s'applique pour la manche suivante")
        game.current_bonus = True
      else:
        master_prize = games_config["game5"]["prize"]
        master_prize_with_bonus = games_config["game5"]["prize"] \
                      + games_config["game5"]["bonus"]
        game.engine.log(
           "Tous les joueurs ont choisi un prix différent "\
          f"donc le gros lot passe de {master_prize} "\
          f"à {master_prize_with_bonus} Pièces.")


class Game5(Game):
  def __init__(game, engine):
    super().__init__(engine)
    game.game_nb = 5
    game.config = games_config["game5"]
    game.propositions = [[0]*5 for _ in range(3)]
    game.quiz = quiz.copy()
    game.question_id = -1
    game.is_done_stars = [False]*5
    game.answers = [None]*4
    game.is_answer_correct = [None]*4
      
  def set_master(game):
    all_bonuses = game.engine.games[4].total_bonuses == 3
    game.jackpot = game.config["prize"] + all_bonuses * game.config["bonus"]
    stars = [player.stars for player in game.players]
    game.engine.log(
       "Le nombre d'étoiles pour chaque joueur est "\
      f"respectivement : {stars}.")
    if stars.count(max(stars)) == 1:
      master_id = np.argmax(stars)
      game.master = game.players[master_id]
      game.quiz.pop(master_id)
      game.other_players = game.master.other_players
      for i in range(3):
        game.choices[i][master_id] = 0
      game.master.flouze += game.jackpot
      game.engine.log(
        f"{game.master.name} a le plus d'étoiles et remporte ainsi "\
        f"la somme de {game.jackpot} Pièces pour le cinquième jeu.")
      for player in game.other_players:
        player.message = \
          f"{game.master.name} a le plus d'étoiles et est ainsi "\
          f"en possesion de la somme de {game.jackpot} {icons['coin']} "\
           "pour le 5ème jeu"
      game.master.message = \
          "Vous avez le plus d'étoiles et êtes ainsi en possesion de "\
        f"la somme de {game.jackpot} {icons['coin']} pour le 5ème jeu."
      game.next_question()
    else:
      game.engine.log(
        "Dû à l'égalité d'étoiles, personne ne remporte "\
        "le gros lot et le cinquième jeu est annulé")
      for player in game.players:
        player.message = "Dû à l'égalité d'étoiles, "\
                         "personne ne remporte le gros lot "\
                         "et le cinquième jeu est annulé."
      game.end()
  
  @property
  def current_proposition(game):
    round_id = game.current_round_id
    return game.propositions[round_id]

  @property
  def current_guesser(game):
    return game.other_players[game.question_id]

  @property
  def current_question(game):
    return game.quiz[game.question_id]

  @property
  def current_answer(game):
    return game.answers[game.question_id]
  @current_answer.setter
  def current_answer(game, answer):
    game.answers[game.question_id] = answer
    player = game.other_players[game.question_id]
    game.engine.log(f"{player.name} a donné la réponse {answer} "\
               f"à la question : '{game.current_question[1][0]}'.")
    game.next_question()
    game.engine.save_data()
    game.engine.refresh_monitoring()
  
  def next_question(game):
    game.question_id += 1
    if game.question_id == 4:
      for player in game.other_players:
        player.message = \
          f"Veuillez attendre la proposition de {game.master.name} ..."
        player.emit("refresh", None)
      return
    guessers = game.other_players.copy()
    guessers.pop(game.question_id)
    for player, question in zip(guessers, game.current_question[0]):
      player.question = question
    if game.question_id:
      for player in game.other_players:
        player.emit("refresh", None)
  
  def make_proposition(game, amounts):
    for i, (remittee, amount) in enumerate(zip(game.other_players, amounts)):
      game.current_proposition[i] = amount
      game.engine.log(f"{game.master.name} a proposé {amount} Pièces "\
                      f"à {remittee.name}.")
      remittee.message = \
        f"{game.master.name} vous fait une proposition "\
        f"de {amount} {icons['coin']}"
    game.master.is_done = True
    game.engine.next_page()
  
  def set_choice(game, player, decision):
    game.current_choices[player.ID] = decision == "accepté"
    game.engine.log(f"{player.name} a {decision} "\
                    f"la proposition de {game.master.name}.")
    player.is_done = True
  
  def logic(game):
    if sum(game.current_choices) >= 3:
      game.engine.log("La proposition a été acceptée par la majorité.")
      game.master.message = "Votre proposition a été acceptée par la majorité."
      for i, player in enumerate(game.other_players):
        offer = game.current_proposition[i]
        game.master.flouze -= offer
        player.flouze += offer
        player.message = \
           "La proposition à été acceptée par la majorité des joueurs."
        if offer >= 0:
          player.message += Markup(
            f"<br>Vous avez reçu {offer} {icons['coin']} "\
            f"de {game.master.name}.")
        else:
          player.message +=  Markup(
            f"<br>Vous vous êtes fait racketter {-offer} {icons['coin']} "\
            f"par {game.master.name}.")
      game.end()
    else:
      if game.current_round_id == 2:
        prize = games_config["game5"]["prize"] + \
            (game.bonuses == 3) * games_config["game5"]["bonus"]
        game.master.flouze -= prize
        game.engine.log("La proposition a été refusée par la majorité."\
          f"Les {prize} Pièces sont retirées à {game.master.name}.")
        game.master.message = \
          f"Votre dernière proposition a été refusée par "\
          f"la majorité. Les {prize} {icons['coin']} vous sont donc retirées."
        for player in game.other_players:
          player.message = \
            f"Aucun accord n'a été trouvé après ces 3 essais donc "\
            f"{game.master.name} ne remporte pas les "\
            f"{prize} {icons['coin']}."
        game.end()
      else:
        game.engine.log("La proposition a été refusée par la majorité.")
        game.master.message = \
          "Votre proposition a été refusée par la majorité !"
        for player in game.other_players:
          player.message = \
            "La proposition à été refusée par au moins 2 joueurs.<br>"\
            "En attente d'une nouvelle proposition..."
  
  def end(game):
    for player in game.players:
      game.engine.log(
        f"{player.name} repart avec {player.flouze} Pièces, ce qui "\
        f"correspond à {str(player.flouze / 10).rstrip('0').rstrip('.')} €.")
      player.message += Markup(
        f"<br>Vous repartez donc avec {player.flouze} {icons['coin']}, ce qui "\
        f"correspond à {str(player.flouze / 10).rstrip('0').rstrip('.')} €.")
    game.engine.log("FIN DU JEU")
    game.engine.iterator = len(pages) - 1
