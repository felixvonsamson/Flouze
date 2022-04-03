from flask import request, session
from flask import render_template, redirect, url_for, flash
from flask import Blueprint
from functools import partial
from website import engine

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
  player = engine.players[session["ID"]]
  render_template_ctx = partial(render_template, engine=engine, player=player)
  if request.method == "POST":
    if not engine.use_nonce(request.form.get("envoyer")):
      return redirect(url_for("views.home"))
    receiver_level = request.form.get("destinataire")
    if receiver_level == None:
      flash_error("Veuillez choisir un destinataire !")
      return render_template_ctx("faire_un_don.jinja")
    amount = request.form.get("montant")
    if amount == "":
      flash_error("Veuiller indiquer un montant !")
      return render_template_ctx("faire_un_don.jinja")
    receiver_level = int(receiver_level)
    receiver = player.other_players[receiver_level]
    amount = int(amount)
    if amount <= 0:
      flash_error("Le montant à envoyer ne peut pas être negatif ou nul !")
      return render_template_ctx("faire_un_don.jinja")
    if amount > player.flouze:
      flash_error("Le montant indiqué dépasse votre solde !")
      return render_template_ctx("faire_un_don.jinja")
    player.send_money(receiver, amount)
    return redirect(url_for("views.home"))
  return render_template_ctx("faire_un_don.jinja")

@views.route("/partager_profit", methods=["GET", "POST"])
def partager_profit():
  player = engine.players[session["ID"]]
  render_template_ctx = partial(render_template, engine=engine, player=player)
  if request.method == "POST":
    if not engine.use_nonce(request.form.get("envoyer")):
      return redirect(url_for("views.home"))
    amounts = []
    if player.last_profit < 0 : 
      for receiver in player.other_players:
        amount = request.form.get(receiver.name)
        amount = 0 if amount == "" else int(amount)
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
        amount = request.form.get(receiver.name)
        amount = 0 if amount == "" else int(amount)
        if amount < 0:
          flash_error("Vous ne pouvez pas envoiyer des montants négatifs !")
          return render_template_ctx("partager.jinja")
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
  player = engine.players[session["ID"]]
  render_template_ctx = partial(render_template, engine=engine, player=player)
  if request.method == "POST" and "don_etoiles" not in request.form:
    if not engine.use_nonce(request.form.get("envoyer")):
      return redirect(url_for("views.home"))
    receiver_level = request.form.get("destinataire")
    amount = request.form.get("quantité")
    if receiver_level == None:
      flash_error("Veuiller choisir un destinataire !")
      return render_template_ctx("don_etoiles.jinja")
    if amount == "":
      flash_error("Veuiller indiquer un nombre d'étoiles !")
      return render_template_ctx("don_etoiles.jinja")
    receiver_level = int(receiver_level)
    amount = int(amount)
    if amount <= 0:
      flash_error(
        "Le nombre d'étoiles à envoyer ne peut pas être negatif ou nul")
      return render_template_ctx("don_etoiles.jinja")
    if amount > player.stars:
      flash_error("Vous n'avez pas assez d'étoiles")
      return render_template_ctx("don_etoiles.jinja")
    receiver = player.other_players[receiver_level]
    player.send_stars(receiver, amount)
    return redirect(url_for("views.home"))
  return render_template_ctx("don_etoiles.jinja")
  

@views.route("/", methods=["GET", "POST"])
def home():
  player = engine.players[session["ID"]]
  render_template_ctx = partial(render_template, engine=engine, player=player)
  game = engine.current_game
  if request.method == "POST":

    if "jeu1" in request.form:
      if not game.is_allowed_to_play(player, 1):
        return redirect(url_for("views.home"))
      tickets = request.form.get("tickets")
      if tickets == None:
        flash_error("Veuiller faire un choix !")
        return render_template_ctx(engine.current_page["url"])
      tickets = int(tickets)
      player.choice = tickets
      engine.log(f"{player.name} a choisis {tickets} tickets.")
      player.flash_message(f"Vous avez choisis {tickets} tickets.")
      player.is_done = True

    elif "jeu2" in request.form:
      if not game.is_allowed_to_play(player, 2):
        return redirect(url_for("views.home"))
      if "choice" not in request.form:
        flash_error("Veuiller choisir un nombre !")
        return render_template_ctx(engine.current_page["url"])
      player.choice = int(request.form["choice"])
      engine.log(f"{player.name} a choisis le nombre {player.choice}.")
      player.flash_message(f"Vous avez choisis le nombre {player.choice}.")
      player.is_done = True

    elif "jeu3" in request.form:
      if not game.is_allowed_to_play(player, 3):
        return redirect(url_for("views.home"))
      amount = request.form.get("montant")
      if amount == "":
        flash_error("Veuiller indiquer un montant !")
        return render_template_ctx(engine.current_page["url"])
      amount = int(amount)
      if amount < 0:
        flash_error("Le montant à investir ne peut pas être negatif !")
        return render_template_ctx(engine.current_page["url"])
      if amount > player.flouze:
        flash_error("Le montant indiqué dépasse votre solde !")
        return render_template_ctx(engine.current_page["url"])
      player.flouze -= amount
      player.choice = amount
      engine.log(f"{player.name} a versé {amount} Pièces dans le pot commun")
      player.flash_message(
        f"Vous avez versé {amount} {icons['coin']} dans le pot commun")
      player.is_done = True
        
    elif "jeu4" in request.form:
      if not game.is_allowed_to_play(player, 4):
        return redirect(url_for("views.home"))
      if "choice" not in request.form:
        flash_error("Veuiller choisir un prix !")
        return render_template_ctx(engine.current_page["url"])
      player.choice = int(request.form["choice"])
      prizes = game.current_prizes
      prize = prizes[player.choice]
      if prize == "star":
        if player.choice == 3 :
          engine.log(f"{player.name} a choisis la deuxième étoile.")
        else :
          engine.log(f"{player.name} a choisis l'etoile.")
        player.flash_message(f"Vous avez choisis le prix : {icons['star']}")
      else:
        engine.log(f"{player.name} a choisis le prix : {prize} Pièces")
        player.flash_message(
          f"Vous avez choisis le prix : {prize} {icons['coin']}")
      player.is_done = True
    
    elif "don_etoiles" in request.form:
      assert request.form["don_etoiles"] == "terminer"
      player.is_done = True

    elif "jeu5" in request.form:
      assert request.form["jeu5"] in [
        "proposition", "nouvelle_proposition", 
        "refuser", "accepter", "quiz_reponse"]
      
      if request.form["jeu5"] == "quiz_reponse":
        answer = request.form.get("réponse")
        engine.log(f"{player.name} a donner la réponse {answer} au quiz")
        game.current_answer = answer
      
      elif request.form["jeu5"] == "proposition":
        if not game.is_allowed_to_play(player, 5):
          return redirect(url_for("views.home"))
        total = 0
        for other_player in game.other_players:
          amount = request.form.get(other_player.name)
          if amount == "":
            flash_error("Veuiller indiquer un montant pour tous les joueurs !")
            return render_template_ctx("Jeu5-proposition.jinja")
          amount = int(amount)
          if amount + other_player.flouze < 0:
            flash_error(f"{other_player.name} ne peut pas accepter votre "\
                         "proposition car il n'a pas assez d'argent !")
            return render_template_ctx("Jeu5-proposition.jinja")
          total += amount
        if total > player.flouze:
          flash_error(
            "Les propositions que vous avez faites dépasse vos moyens !")
          return render_template_ctx("Jeu5-proposition.jinja")
        for i, other_player in enumerate(game.other_players):
          amount = int(request.form.get(other_player.name))
          amount = int(amount)
          game.current_proposition[i] = amount
          other_player.message = \
            f"{player.name} vous fait une proposition "\
            f"de {amount} {icons['coin']}"
        player.is_done = True
        engine.next_page()
      
      elif request.form["jeu5"] in ["refuser", "accepter"]:
        if not game.is_allowed_to_play(player, 5):
          return redirect(url_for("views.home"))
        player.choice = request.form["jeu5"] == "accepter"
        player.is_done = True
      
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
