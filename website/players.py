import datetime
from platform import platform
from flask import Markup, flash

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

    player.last_profit = 0
    player.messages = []

  @property
  def choice(player):
    return player.engine.current_game.current_choices[player.ID]
  @choice.setter
  def choice(player, choice):
    player.engine.current_game.current_choices[player.ID] = choice

  @property
  def is_done(player):
    return player.engine.current_stage[1] in [1, 2, 3] \
           and player.engine.current_game.current_done[player.ID]
  @is_done.setter
  def is_done(player, is_done):
    player.engine.current_game.current_done[player.ID] = is_done
    current_game = player.engine.current_game
    if not current_game.is_everyone_done:
      current_game.update_waiting_count()
    else:
      player.engine.next_page()
    player.engine.refresh_monitoring()

  def send_message(player, message):
    socketio = player.engine.socketio
    player.messages.append((datetime.datetime.now(), message))
    socketio.emit('message', message, room=player.sid)

  def send_money(player, receiver, amount):
    assert (player.flouze >= amount)

    player.flouze -= amount
    receiver.flouze += amount

    player.engine.log(f"{player.name} a fait un don de {amount} Pièces à "\
                      f"{receiver.name}.")

    updates = [("flouze", receiver.flouze)]
    player.engine.update_fields(updates, [receiver])

    flash(Markup(
      f"Vous avez envoyé {amount} {icons['coin']}"\
      f" &nbsp; à {receiver.name}."), category="success")
    
    receiver.send_message(
      f"Vous avez reçu {amount} {icons['coin']} &nbsp; "\
      f"de la part de {player.name}.")

    player.engine.save_data()


  def send_star(player, receiver, sent_stars):
    assert (player.stars >= sent_stars)

    player.stars -= sent_stars
    receiver.stars += sent_stars

    player.engine.log(
      f"{player.name} a légué {sent_stars} "\
      f"étoile({'s' if sent_stars > 1 else ''}) à {receiver.name}.")

    updates = [(f"player{player.ID}_star", f" {player.stars}"),
           (f"player{receiver.ID}_star", f" {receiver.stars}")]
    player.engine.update_fields(updates)

    flash(Markup(
      f"Vous avez envoyé {sent_stars} {icons['star']} "\
      f"à {receiver.name}."), category="success")

    receiver.send_message(
      f"Vous avez reçu {sent_stars} {icons['star']}"\
      f"de la part de {player.name}.")

    player.engine.save_data()


  def share_profit(player, amounts):
    assert player.last_profit
    assert (sum(amounts) <= player.last_profit)
    assert (sum(amounts) <= player.flouze)
    for receiver, amount in zip(player.other_players, amounts):
      if amount:
        player.send_money(receiver, amount)
    player.last_profit = None
