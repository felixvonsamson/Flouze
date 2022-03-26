import datetime
from flask import Markup

from .html_icons import icons

class Player(object):
  def __init__(player, ID, name, password, main_color, sec_color, engine):
    player.engine = engine
    player.ID = ID
    player.sid = None
    player.name = name
    player.password = password
    player.color = main_color
    player.sec_color = sec_color
    player.flouze = 0
    # Dans le jeu 3 l'argent est mis de coté
    player.saved_flouze = 0
    player.stars = 0

    player.last_profit = None
    player.__message = None
    player.messages = []

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
    player.engine.refresh_monitoring()

  def send_message(player, message, timeout=30, emit=False):
    message = Markup(message)
    socketio = player.engine.socketio
    now = datetime.datetime.now()
    player.messages.append((now, now + timeout, message))
    if emit:
      socketio.emit("message", message, room=player.sid)
  
  @property
  def message(player):
    return player.__message
  @message.setter
  def message(player, message):
    player.__message = Markup(message)
    player.send_message(message, timeout=-1)
  
  @property
  def messages_to_show(player):
    now = datetime.datetime.now()
    return [message for _, limit, message in player.messages if limit <= now]


  def send_money(player, receiver, amount):
    assert (player.flouze >= amount)

    player.flouze -= amount
    receiver.flouze += amount

    player.engine.log(
      f"{player.name} a fait un don de {amount} Pièces à {receiver.name}.")

    updates = [("flouze", receiver.flouze)]
    player.engine.update_fields(updates, [receiver])

    player.send_message(
      f"Vous avez envoyé {amount} {icons['coin']} &nbsp; à {receiver.name}.")
    
    receiver.send_message(
      f"Vous avez reçu {amount} {icons['coin']} &nbsp; "\
      f"de la part de {player.name}.", emit=True)

    player.engine.save_data()


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

    player.send_message(
      f"Vous avez envoyé {sent_stars} {icons['star']} à {receiver.name}.")

    receiver.send_message(
      f"Vous avez reçu {sent_stars} {icons['star']}"\
      f"de la part de {player.name}.", emit=True)

    player.engine.save_data()


  def share_profit(player, amounts):
    assert player.last_profit
    assert (sum(amounts) <= player.last_profit)
    assert (sum(amounts) <= player.flouze)
    for receiver, amount in zip(player.other_players, amounts):
      if amount:
        player.send_money(receiver, amount)
    player.last_profit = None
