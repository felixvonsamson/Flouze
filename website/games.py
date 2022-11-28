import random
import numpy as np
from abc import ABC, abstractmethod
from flask import Markup

from .html_icons import icons
from .pages_ordering import pages
from .text import color_names, game_names, quiz, logs_txt, player_txt

games_config = {
  "colors": {
    "background": "2.jpg", 
  }, 
  "game1": {
    "title": game_names["game 1"], 
    "background": "10.jpg", 
    "prizes": [200, 400, 600], 
    "3rd_round_stars": 1
  }, 
  "game2": {
    "title": game_names["game 2"], 
    "background": "9.jpg", 
    "prizes": [50, 100, 150], 
    "3rd_round_stars": 2
  }, 
  "game3": {
    "title": game_names["game 3"], 
    "background": "8.jpg", 
    "initial_flouze": 100, 
    "interests": [1.2, 1.5, 2], 
    "3rd_round_stars": 2
  }, 
  "game4": {
    "title": game_names["game 4"], 
    "background": "6.jpg", 
    "prizes": [[[150, 100, 50, 0, "star"]], 
               [[350, 150, 0, -50, "star"], 
                [500, 200, 0, -100, "star"]], 
               [[500, 250, -150, "star", "star"], 
                [700, 300, -250, "star", "star"], 
                [900, 400, -400, "star", "star"]]]
  }, 
  "game5": {
    "title": game_names["game 5"], 
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
  (["Quel __ __ nom __ _____ de ____ __ la ______ ______ LTT ?", 
    "____ est __ ___ de _____ __ Linus, __ __ chaine ______ ___ ?", 
    "____ __ le ___ __ famille __ ____ de __ ______ Youtube ___ ?"], 
   ["Quel est le nom de famille de Linus, de la chaine LTT ?", 
    "Sebastian"])
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
    game.players = engine.players
    game.game_nb = 0
    game.config = games_config["colors"]
    game.colors = list(color_names.keys())
    game.owner = {}
    game.choices = [[None]*5]
    game.is_done = [[False]*5]
  
  def set_choice(game, player, color):
    updates = []
    last_choice  = game.choices[0][player.ID]
    if last_choice != None :
      game.owner.pop(last_choice)
      updates.append((last_choice, ""))
    game.owner[color] = player
    game.choices[0][player.ID] = color
    updates.append((color, player.name))
    game.engine.update_fields(updates)
    player.is_done = True
  
  def logic(game):
    pass

  def end(game):
    engine = game.engine
    for player in game.players:
      color = game.choices[0][player.ID]
      player.color = color
      engine.log(logs_txt["color choice"][engine.lang_id].format(
        name = player.name, color = player.color))
      player.send_message(player_txt["color selected"][player.lang_id].format(
        color = player.color))
  

class Game1(Game):
  def __init__(game, engine):
    super().__init__(engine)
    game.game_nb = 1
    game.config = games_config["game1"]
  
  def set_choice(game, player, tickets):
    game.current_choices[player.ID] = tickets
    game.engine.log(logs_txt["tickets choice"][game.engine.lang_id].format(
      name = player.name, tickets = tickets))
    player.flash_message(player_txt["chosen tickets"][player.lang_id].format(
      tickets = tickets))
    player.is_done = True
  
  def logic(game):
    assert game.is_everyone_done
    engine = game.engine
    choices = game.current_choices
    lottery = []
    for player, nb_tickets in zip(game.players, choices):
      lottery += [player] * nb_tickets
      player.message = player_txt["chosen tickets"][player.lang_id].format(
        smiley = icons['sad'])
    if len(lottery) > 0:
      winner = random.choice(lottery)
      prize = game.config["prizes"][game.current_round_id]
      prize //= len(lottery)
      winner.flouze += prize
      winner.last_profit = prize
      engine.log(logs_txt["lottery winner"][engine.lang_id].format(
        name = winner.name, prize = prize))
      winner.message = player_txt["lottery winner"][winner.lang_id].format(
        prize = prize, coin = icons['coin'])
      if game.current_round_id == 2:
        won_stars = game.config["3rd_round_stars"]
        winner.stars += won_stars
        engine.log(logs_txt["last round winner"][engine.lang_id].format(
          name = winner.name, stars = won_stars))
        winner.message += Markup(
          player_txt["last round winner"][winner.lang_id].format(
          stars = won_stars, star = icons['star']))
    else:
      engine.log(logs_txt["no lottery winner"][engine.lang_id])
      if game.current_round_id == 2:
        engine.log(logs_txt["no stars"][engine.lang_id])


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
    game.engine.log(logs_txt["number choice"][game.engine.lang_id].format(
      name = player.name, number = number))
    player.flash_message(player_txt["chosen number"][player.lang_id].format(
      number = number))
    player.is_done = True
  
  def logic(game):
    assert game.is_everyone_done
    engine = game.engine
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
      engine.log(logs_txt["winner number"][engine.lang_id].format(
        name = winner.name, prize = prize))
      winner.message = player_txt["winner number"][winner.lang_id].format(
        prize = prize, coin = icons['coin'])
      for player in winner.other_players:
        player.message = player_txt["looser number"][player.lang_id]
      if round_id == 2:
        won_stars = game.config["3rd_round_stars"]
        winner.stars += won_stars
        engine.log(logs_txt["last round winner"][engine.lang_id].format(
          name = winner.name, stars = won_stars))
        winner.message += Markup(
          player_txt["last round winner"][winner.lang_id].format(
            stars = won_stars, star = icons['star']))
    else:
      engine.log(logs_txt["no winner"][engine.lang_id])
      for player in game.players:
        player.message = player_txt["no winner"][player.lang_id]
      if round_id == 2:
        engine.log(logs_txt["no stars"][engine.lang_id])


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
    game.engine.log(logs_txt["money set aside"][game.engine.lang_id].format(
      flouze = initial_flouze))
  
  def set_choice(game, player, amount):
    player.flouze -= amount
    game.current_choices[player.ID] = amount
    game.engine.log(
      logs_txt["investment in common pot"][game.engine.lang_id].format(
      name = player.name, amount = amount))
    player.flash_message(player_txt["flouze invested"][player.lang_id].format(
      amount = amount, coin = icons['coin']))
    player.is_done = True
  
  def logic(game):
    assert game.is_everyone_done
    engine = game.engine
    inputs = game.current_choices
    common_pot = sum(inputs)
    if game.sabotage and common_pot>299 :
      common_pot -= 120
      engine.log(logs_txt["sabotage"][engine.lang_id].format(
        common_pot = common_pot))
      game.sabotage = False

    interest = game.config["interests"][game.current_round_id]
    prize = int(common_pot * interest  // 5)
    engine.log(logs_txt["pot distribution"][engine.lang_id].format(
      total = 5 * prize, prize = prize))

    for player, shared in zip(game.players, game.current_choices):
      player.flouze += prize
      game.real_gain[player.ID] += prize - shared
      player.message = player_txt["return on investment"][player.lang_id]\
        .format(prize = prize, coin = icons['coin'])

    if game.current_round_id == 2:
      winner_id = np.argmax(game.real_gain)
      winner = game.players[winner_id]
      engine.log(logs_txt["benefits"][engine.lang_id].format(
        benefit = game.real_gain))
      if game.real_gain.count(max(game.real_gain)) == 1:
        won_stars = game.config["3rd_round_stars"]
        winner.stars += won_stars
        engine.log(logs_txt["largest benefit"][engine.lang_id].format(
          name = winner.name, stars = won_stars))
        winner.message = player_txt["made the most money"][winner.lang_id]\
          .format(prize = prize, coin = icons['coin'], stars = won_stars,
          star = icons['star'])
      else:
        engine.log(logs_txt["tie no stars"][engine.lang_id])

  def end(game):
    for player in game.players:
      player.flouze += player.saved_flouze
      player.saved_flouze = 0
    game.engine.log(logs_txt["money returned"][game.engine.lang_id])


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
    engine = game.engine
    game.current_choices[player.ID] = prize_id
    prizes = game.current_prizes
    prize = prizes[prize_id]
    if prize == "star":
      if player.choice == 3 :
        engine.log(logs_txt["chosen star2"][engine.lang_id].format(
          name = player.name))
      else :
        engine.log(logs_txt["chosen star"][engine.lang_id].format(
          name = player.name))
      player.flash_message(player_txt["chosen star"][player.lang_id].format(
        star = icons['star']))
    else:
      engine.log(logs_txt["chosen prize"][engine.lang_id].format(
        name = player.name, prize = prize))
      player.flash_message(player_txt["chosen prize"][player.lang_id].format(
        prize = prize, coin = icons['coin']))
    player.is_done = True
  
  def logic(game):
    assert game.is_everyone_done
    engine = game.engine
    # compte le nombre de choix uniques
    choices = game.current_choices
    values, count = np.unique(choices, return_counts=True)
    unique_choices = set(values[np.where(count == 1)])
    for player, choice in zip(game.players, choices):
      if choice in unique_choices:
        prize = game.current_prizes[choice]
        if prize == "star":
          player.stars += 1
          engine.log(logs_txt["won star"][engine.lang_id].format(
            name = player.name))
          player.message = player_txt["won star"][player.lang_id].format(
            star = icons['star'])
        else:
          player.flouze += prize
          player.last_profit = prize
          engine.log(logs_txt["won prize"][engine.lang_id].format(
            name = player.name, prize = prize))
          player.message = player_txt["won prize"][player.lang_id].format(
            prize = prize, coin = icons['coin'])
      else:
        player.message = player_txt["prize not won"][player.lang_id]

    if len(unique_choices) == 5:
      game.current_bonus = True
      if game.current_round_id in [0, 1]:
        engine.log(logs_txt["bonus"][engine.lang_id])
      else:
        master_prize = games_config["game5"]["prize"]
        master_prize_with_bonus = games_config["game5"]["prize"] \
                      + games_config["game5"]["bonus"]
        engine.log(logs_txt["bonus round 3"][engine.lang_id].format(
          prize = master_prize, bonus = master_prize_with_bonus))


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
    engine = game.engine
    all_bonuses = game.engine.games[4].total_bonuses == 3
    game.jackpot = game.config["prize"] + all_bonuses * game.config["bonus"]
    stars = [player.stars for player in game.players]
    engine.log(logs_txt["star count"][engine.lang_id].format(stars = stars))
    if stars.count(max(stars)) == 1:
      master_id = np.argmax(stars)
      game.master = game.players[master_id]
      game.quiz.pop(master_id)
      game.other_players = game.master.other_players
      for i in range(3):
        game.choices[i][master_id] = 0
      game.master.flouze += game.jackpot
      engine.log(logs_txt["most stars"][engine.lang_id].format(
        name = game.master.name, jackpot = game.jackpot))
      for player in game.other_players:
        player.message = player_txt["starmaster announcement"][player.lang_id]\
          .format(name = game.master.name, jackpot = game.jackpot,
          coin = icons['coin'])
      game.master.message = player_txt["you are the starmaster"]\
        [game.master.lang_id].format(jackpot = game.jackpot,
        coin = icons['coin'])
      game.next_question()
    else:
      engine.log(logs_txt["tie star"][engine.lang_id])
      for player in game.players:
        player.message = player_txt["tie"][player.lang_id]
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
    game.engine.log(logs_txt["awnser proposal"][game.engine.lang_id].format(
      name = player.name, answer = answer, 
      question = game.current_question[1][0]))
    game.next_question()
    game.engine.save_data()
    game.engine.refresh_monitoring()
  
  def next_question(game):
    game.question_id += 1
    if game.question_id == 4:
      for player in game.other_players:
        player.message = player_txt["wait"][player.lang_id].format(
          name = game.master.name)
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
    engine = game.engine
    for i, (remittee, amount) in enumerate(zip(game.other_players, amounts)):
      game.current_proposition[i] = amount
      engine.log(logs_txt["gamemaster offer"][engine.lang_id].format(
        gamemaster = game.master.name, amount = amount, name = remittee.name))
      remittee.message = player_txt["offer"][remittee.lang_id].format(
        name = game.master.name, amount = amount, coin = icons['coin'])
    game.master.is_done = True
    engine.next_page()
  
  def set_choice(game, player, decision):
    game.current_choices[player.ID] = decision == "accepté"
    game.engine.log(logs_txt["offer decision"][game.engine.lang_id].format(
      gamemaster = game.master.name, decision = decision, name = player.name))
    player.is_done = True
  
  def logic(game):
    engine = game.engine
    if sum(game.current_choices) >= 3:
      engine.log(logs_txt["offer accepted"][engine.lang_id])
      game.master.message = player_txt["your offer is accepted"]\
        [game.master.lang_id]
      for i, player in enumerate(game.other_players):
        offer = game.current_proposition[i]
        game.master.flouze -= offer
        player.flouze += offer
        player.message = player_txt["offer accepted"][player.lang_id]
        if offer >= 0:
          player.message += Markup(player_txt["offer received"][player.lang_id]\
            .format(offer = offer, coin = icons['coin'],
            name = game.master.name))
        else:
          player.message +=  Markup(player_txt["lost flouze"][player.lang_id]\
            .format(loss = -offer, coin = icons['coin'],
            name = game.master.name))
      game.end()
    else:
      if game.current_round_id == 2:
        game.master.flouze -= game.jackpot
        engine.log(logs_txt["last offer rejected"][engine.lang_id].format(
          name = game.master.name, jackpot = game.jackpot))
        game.master.message = player_txt["your last offer is declined"]\
          [game.master.lang_id].format(jackpot = game.jackpot,
          coin = icons['coin'])
        for player in game.other_players:
          player.message = player_txt["last offer declined"][player.lang_id]\
            .format(jackpot = game.jackpot, coin = icons['coin'],
            name = game.master.name)
        game.end()
      else:
        engine.log(logs_txt["offer rejected"][engine.lang_id])
        game.master.message = player_txt["your offer is declined"]\
          [game.master.lang_id]
        for player in game.other_players:
          player.message = player_txt["offer declined"][player.lang_id].format(
            players = int(len(game.players)/2))
  
  def end(game):
    engine = game.engine
    for player in game.players:
      engine.log(logs_txt["final earnings"][engine.lang_id].format(
          name = player.name, flouze = player.flouze))
      player.message += Markup(player_txt["final earnings"][player.lang_id]\
        .format(flouze = player.flouze, coin = icons['coin']))
    engine.log(logs_txt["end"][engine.lang_id])
    engine.iterator = len(pages) - 1
