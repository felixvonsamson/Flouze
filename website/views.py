from flask import current_app, request, session
from flask import render_template, redirect, url_for, flash
from flask import Blueprint
from functools import partial

from .html_icons import icons

views = Blueprint("views", __name__)
flash_error = partial(flash,  category="error")

@views.before_request
def check_user():
  if session["ID"] == "admin":
    return redirect(url_for("monitoring.home"))
  assert session["ID"] in range(5)


@views.route("/faire_un_don", methods=("GET", "POST"))
def donner_flouze():
  engine = current_app.config["engine"]
  player = engine.players[session["ID"]]
  render_template_ctx = partial(render_template, engine=engine, player=player)
  if request.method == "POST":
    if not engine.use_nonce(request.form.get("envoyer")):
      return redirect(url_for("views.home"))
    receiver_level = int(request.form.get("destinataire"))
    amount = int(request.form.get("montant"))
    receiver = player.other_players[receiver_level]
    if amount > player.flouze:
      flash_error("Le montant indiqué dépasse votre solde !")
      return render_template_ctx("faire_un_don.jinja")
    player.send_money(receiver, amount)
    return redirect(url_for("views.home"))
  return render_template_ctx("faire_un_don.jinja")

@views.route("/partager_profit", methods=["GET", "POST"])
def partager_profit():
  engine = current_app.config["engine"]
  player = engine.players[session["ID"]]
  render_template_ctx = partial(render_template, engine=engine, player=player)
  if request.method == "POST":
    if not engine.use_nonce(request.form.get("envoyer")):
      return redirect(url_for("views.home"))
    amounts = []
    if player.last_profit < 0 : 
      for receiver in player.other_players:
        amount = int(request.form.get(receiver.name))
        if amount > 0:
          flash_error("Si vous vouler donner de l'argent veuillez utiliser "\
                      "le boutton 'faire un don'...")
          return render_template_ctx("partager.jinja")
        amounts.append(amount)
      if sum(amounts) < player.last_profit:
        flash_error(
          "Vous ne pouvez pas réclamer plus que ce que vous avez perdu !")
        return render_template_ctx("partager.jinja")
    else:
      for receiver in player.other_players:
        amount = int(request.form.get(receiver.name))
        amounts.append(amount)
      if sum(amounts) > player.last_profit:
        flash_error(
          "Vous ne pouvez pas donner plus que ce que vous avez reçu !")
        return render_template_ctx("partager.jinja")
      if sum(amounts) > player.flouze:
        flash_error(
          "Vous ne pouvez pas donner plus que ce que vous avez avez !")
        return render_template_ctx("partager.jinja")
    player.share_profit(amounts)
    return redirect(url_for("views.home"))
  return render_template_ctx("partager.jinja")

@views.route("/donner_des_etoiles", methods=("GET", "POST"))
def donner_etoiles():
  engine = current_app.config["engine"]
  player = engine.players[session["ID"]]
  render_template_ctx = partial(render_template, engine=engine, player=player)
  if request.method == "POST":
    if not engine.use_nonce(request.form.get("envoyer")):
      return redirect(url_for("views.home"))
    receiver_level = int(request.form.get("destinataire"))
    amount = int(request.form.get("quantité"))
    if amount > player.stars:
      flash_error("Vous n'avez pas assez d'étoiles")
      return render_template_ctx("don_etoiles.jinja")
    receiver = player.other_players[receiver_level]
    player.send_stars(receiver, amount)
    return redirect(url_for("views.home"))
  return render_template_ctx("don_etoiles.jinja")
  

@views.route("/", methods=["GET", "POST"])
def home():
  engine = current_app.config["engine"]
  player = engine.players[session["ID"]]
  render_template_ctx = partial(render_template, engine=engine, player=player)
  game = engine.current_game
  if request.method == "POST":

    if "jeu1" in request.form:
      if not game.is_allowed_to_play(player, 1):
        return redirect(url_for("views.home"))
      tickets = int(request.form.get("tickets"))
      player.choice = tickets
      

    elif "jeu2" in request.form:
      if not game.is_allowed_to_play(player, 2):
        return redirect(url_for("views.home"))
      player.choice = int(request.form["choice"])

    elif "jeu3" in request.form:
      if not game.is_allowed_to_play(player, 3):
        return redirect(url_for("views.home"))
      amount = int(request.form.get("montant"))
      if amount > player.flouze:
        flash_error("Le montant indiqué dépasse votre solde !")
        return render_template_ctx(engine.current_page["url"])
      player.choice = amount
        
    elif "jeu4" in request.form:
      if not game.is_allowed_to_play(player, 4):
        return redirect(url_for("views.home"))
      player.choice = int(request.form["choice"])
    
    elif "don_etoiles" in request.form:
      assert request.form["don_etoiles"] == "terminer"
      player.is_done = True

    elif "jeu5" in request.form:
      assert request.form["jeu5"] in [
        "proposition", "nouvelle_proposition", 
        "refusé", "accepté", "quiz_reponse"]
      
      if request.form["jeu5"] == "quiz_reponse":
        game.current_answer = request.form.get("réponse")
      
      elif request.form["jeu5"] == "proposition":
        if not game.is_allowed_to_play(player, 5):
          return redirect(url_for("views.home"))
        total = 0
        for other_player in game.other_players:
          amount = int(request.form.get(other_player.name))
          if amount + other_player.flouze < 0:
            flash_error(f"{other_player.name} ne peut pas accepter votre "\
                         "proposition car il n'a pas assez d'argent !")
            return render_template_ctx("Jeu5-proposition.jinja")
          total += amount
        if total > player.flouze:
          flash_error(
            "Les propositions que vous avez faites dépasse vos moyens !")
          return render_template_ctx("Jeu5-proposition.jinja")
        amounts = [int(request.form.get(other_player.name)) 
                   for other_player in game.other_players]
        game.make_proposition(amounts)
      
      elif request.form["jeu5"] in ["refusé", "accepté"]:
        if not game.is_allowed_to_play(player, 5):
          return redirect(url_for("views.home"))
        player.choice = request.form["jeu5"]
      
      elif request.form["jeu5"] == "nouvelle_proposition":
        engine.next_page(refresh=False)
        engine.save_data()

  if engine.current_page["url"] == "Jeu 5":
    if engine.current_page["phase"] == "proposition":
      if player == game.master:
        return render_template_ctx("Jeu5-proposition.jinja")
      elif game.current_round_id == 0 and game.question_id < 4:
        return render_template_ctx("quiz.jinja")
      else:
        return render_template_ctx("results.jinja")
    
    elif engine.current_page["phase"] == "validation":
      if player.is_done:
        return render_template_ctx("en_attente_jeu5.jinja")
      return render_template_ctx("Jeu5-Valider.jinja")
    
    elif engine.current_page["phase"] == "reveal":
      if player == game.master:
        return render_template_ctx("Jeu5-reveal.jinja")
      else:
        return render_template_ctx("results.jinja")

  if "choix" in engine.current_page["url"] and player.is_done:
    return render_template_ctx("en_attente.jinja")
  
  return render_template_ctx(engine.current_page["url"])
