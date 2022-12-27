from datetime import datetime, timedelta
from flask import Markup, flash

from .html_icons import icons

class Player(object):
  def __init__(player, engine, ID, name, password, lang_id=None):
    player.engine = engine
    player.ID = ID
    player.sid = None
    player.name = name
    player.password = password
    player.lang_id = int(lang_id) if lang_id else engine.lang_id
    player.lang_txt = engine.text["languages_name"][player.lang_id]
    player.color = None
    player.flouze = 0
    # Dans le jeu 3 l'argent est mis de coté
    player.saved_flouze = 0
    player.stars = 0
    player.last_profit = 0
    player.last_page = None
    player.__message = None
    player.messages = []
    player.flouze_request = None

  @property
  def choice(player):
    return player.engine.current_game.current_choices[player.ID]
  @choice.setter
  def choice(player, choice):
    player.engine.current_game.set_choice(player, choice)

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
    player.engine.refresh_monitoring()

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

  @property
  def is_sharing_money(player):
    return player.last_page in ["faire_un_don.jinja", "partager.jinja"]

  def send_money(player, receiver, amount, update_sender=False, save=True):
    engine = player.engine
    assert (player.flouze >= amount)
    player.flouze -= amount
    receiver.flouze += amount
    donation_log = engine.text["logs_txt"]["donation"][engine.lang_id].format(
      name = player.name, amount = amount, receiver = receiver.name)
    engine.log(donation_log)
    player.engine.current_game.interactions[player.engine.current_stage].append(
      donation_log)
    updates = [("flouze", receiver.flouze)]
    engine.update_fields(updates, [receiver])
    if update_sender:
      updates = [("flouze", player.flouze)]
      engine.update_fields(updates, [player])
    player.flash_message(engine.text["player_txt"]["sent flouze"]\
      [player.lang_id].format(name = receiver.name, amount = amount,
      coin = icons['coin']))
    receiver.send_message(engine.text["player_txt"]["received flouze"]\
      [receiver.lang_id].format(name = player.name, amount = amount,
      coin = icons['coin']))
    if save:
      engine.save_data()
      engine.refresh_monitoring()

  def request_money(player, receiver, amount):
    receiver.flouze_request = (player, amount)
    claim_log = player.engine.text["logs_txt"]["claim"]\
      [player.engine.lang_id].format(name = player.name, amount = amount,
      donor = receiver.name)
    player.engine.log(claim_log)
    player.engine.current_game.interactions[player.engine.current_stage].append(
      claim_log)
    receiver.send_request(player.engine.text["player_txt"]["flouze claim"]\
      [receiver.lang_id].format(name = player.name, amount = amount,
      coin = icons['coin']))

  def send_stars(player, receiver, sent_stars):
    assert (player.stars >= sent_stars)
    player.stars -= sent_stars
    receiver.stars += sent_stars
    sent_star_log = player.engine.text["logs_txt"]["star donation"]\
      [player.engine.lang_id].format(name = player.name, stars = sent_stars,
      receiver = receiver.name)
    player.engine.log(sent_star_log)
    player.engine.current_game.interactions[player.engine.current_stage].append(
      sent_star_log)
    updates = [(f"player{player.ID}_star", f" {player.stars}"),
               (f"player{receiver.ID}_star", f" {receiver.stars}")]
    player.engine.update_fields(updates)
    player.flash_message(player.engine.text["player_txt"]["sent stars"]\
      [player.lang_id].format(name = receiver.name, stars = sent_stars,
      star = icons['star']))
    receiver.send_message(player.engine.text["player_txt"]["received stars"]\
      [receiver.lang_id].format(name = player.name, stars = sent_stars,
      star = icons['star']))
    player.engine.save_data()
    player.engine.refresh_monitoring()


  def share_profit(player, amounts):
    assert player.last_profit != 0
    for receiver, amount in zip(player.other_players, amounts):
      if amount:
        if player.last_profit < 0 :
          if receiver.flouze >= -amount:
            player.request_money(receiver, -amount)
          else:
            receiver.send_message(player.engine.text["player_txt"]\
              ["not enough money for flouze claim"][receiver.lang_id].format(
                name = player.name, amount = amount, coin = icons['coin']))
        else:
          player.send_money(receiver, amount, save=False)
    player.last_profit = 0
    player.engine.save_data()
    player.engine.refresh_monitoring()
