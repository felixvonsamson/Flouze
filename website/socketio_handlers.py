import datetime
from flask import request, session

def add_handlers(socketio, engine):
  @socketio.on("give_identity")
  def give_identity():
    if session["ID"] == "admin":
      engine.admin_sid = request.sid
    else:
      player = engine.players[int(session["ID"])]
      player.sid = request.sid
  @socketio.on("hide_message")
  def hide_message(message_id):
    player = engine.players[int(session["ID"])]
    player.messages[message_id][1] = datetime.datetime.now()
  @socketio.on("answer_flouze_request")
  def answer_flouze_request(accept):
    player = engine.players[int(session["ID"])]
    requester, amount = player.flouze_request
    if accept: 
      player.send_money(requester, amount, update_sender=True)
    else:
      requester.send_message(
        f"Votre demande à été refusée par {player.name}.", category="error")
    player.requested_flouze = None
  @socketio.on("select_color")
  def select_color(color_id):
    assert color_id in range(5)
    player = engine.players[int(session["ID"])]
    game = engine.current_game
    if game.owner[color_id] :
      if game.owner[color_id] == player :
        player.send_message("Vous avez déjà sélectionné cette couleur.", 
                            category="error", persistant=False)
      else:
        player.send_message(
          f"{game.owner[color_id].name} a été plus rapide que vous !", 
          category="error", persistant=False)
    else:
      player.choice = color_id
