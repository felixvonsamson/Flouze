from datetime import datetime, timedelta
from socket import timeout
from flask import Markup, flash

from .html_icons import icons

class Player(object):
  def __init__(player, ID, name, password, engine):
    player.engine = engine
    player.ID = ID
    player.sid = None
    player.name = name
    player.password = password
    player.__color = None
    player.flouze = 0
    # Dans le jeu 3 l'argent est mis de coté
    player.saved_flouze = 0
    player.stars = 0
    player.last_profit = 0
    player.__message = None
    player.messages = []
    player.flouze_request = None

  @property
  def choice(player):
    return player.engine.current_game.current_choices[player.ID]
  @choice.setter
  def choice(player, choice):
    player.engine.current_game.current_choices[player.ID] = choice

  @property
  def is_done(player):
    return player.engine.current_game.current_done[player.ID]
  @is_done.setter
  def is_done(player, is_done):
    current_game = player.engine.current_game
    current_game.current_done[player.ID] = is_done
    if not current_game.is_everyone_done:
      current_game.update_waiting_count()
    else:
      player.engine.next_page()
    player.engine.save_data()

  @property
  def color(player):
    return player.__color
  @color.setter
  def color(player, color):
    game = player.engine.current_game
    game.owner[color["id"]] = player
    player.__color = color

  def emit(player, *args):
    if player.sid:
      socketio = player.engine.socketio
      socketio.emit(*args, room=player.sid)
  
  def flash_message(player, message, category="message"):
    flash(Markup(message))
    player.send_message(message, category, emit=False, timeout=-1)

  def send_request(player, message, timeout=600):
    player.send_message(message, category="request", timeout=timeout)
  
  def send_message(player, message, category="message", 
                   emit=True, persistant=True, timeout=30):
    message = Markup(message)
    if persistant:
      now = datetime.now()
      timeout = timedelta(seconds=timeout)
      player.messages.append([now, now + timeout, category, message])
    if emit:
      msg_id = len(player.messages) - 1 if persistant else None
      player.emit("message", (msg_id, category, message))
  
  @property
  def message(player):
    return player.__message
  @message.setter
  def message(player, message):
    player.__message = Markup(message)
    player.send_message(message, timeout=-1, emit=False)
  
  @property
  def messages_to_show(player):
    now = datetime.now()
    return [(msg_id, category, message) 
      for msg_id, (_, limit, category, message) in enumerate(player.messages) 
      if now <= limit]


  def send_money(player, receiver, amount, update_sender=False):
    assert (player.flouze >= amount)
    player.flouze -= amount
    receiver.flouze += amount
    player.engine.log(
      f"{player.name} a fait un don de {amount} Pièces à {receiver.name}.")
    updates = [("flouze", receiver.flouze)]
    player.engine.update_fields(updates, [receiver])
    if update_sender:
      updates = [("flouze", player.flouze)]
      player.engine.update_fields(updates, [player])
    player.flash_message(
      f"Vous avez envoyé {amount} {icons['coin']}&nbsp; à {receiver.name}.")
    receiver.send_message(
      f"Vous avez reçu {amount} {icons['coin']}&nbsp; "\
      f"de la part de {player.name}.")
    player.engine.save_data()

  def request_money(player, receiver, amount):
    receiver.flouze_request = (player, amount)
    player.engine.log(
      f"{player.name} réclame {amount} Pièces de la part de {receiver.name}.")
    receiver.send_request(
      f"{player.name} vous réclame {amount} {icons['coin']}.<br> ")


  def send_stars(player, receiver, sent_stars):
    assert (player.stars >= sent_stars)
    player.stars -= sent_stars
    receiver.stars += sent_stars
    player.engine.log(
      f"{player.name} a légué {sent_stars} "\
      f"étoile({'s' if sent_stars > 1 else ''}) à {receiver.name}.")
    updates = [(f"player{player.ID}_star", f" {player.stars}"),
               (f"player{receiver.ID}_star", f" {receiver.stars}")]
    player.engine.update_fields(updates)
    player.flash_message(
      f"Vous avez envoyé {sent_stars} {icons['star']} à {receiver.name}.")
    receiver.send_message(
      f"Vous avez reçu {sent_stars} {icons['star']}"\
      f"de la part de {player.name}.")
    player.engine.save_data()


  def share_profit(player, amounts):
    assert player.last_profit != 0
    for receiver, amount in zip(player.other_players, amounts):
      if amount:
        if player.last_profit < 0 :
          if receiver.flouze >= -amount:
            player.request_money(receiver, -amount)
          else:
            receiver.send_message(
              f"{player.name} vous réclame {amount} {icons['star']} "\
               "mais vous n'avez pas cette somme !")
        else:
          player.send_money(receiver, amount)
    player.last_profit = 0
