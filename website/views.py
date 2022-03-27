from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from website import engine

from .html_icons import icons

views = Blueprint("views", __name__)

@views.before_request
def check_user():
  if "ID" not in session :
    return redirect(url_for("auth.login"))
  if session["ID"] == "admin":
    return redirect(url_for("monitoring.home"))
  assert session["ID"] in range(5)


@views.route("/faire_un_don", methods=("GET", "POST"))
def donner_flouze():
  player = engine.players[session["ID"]]
  if request.method == "POST":
    receiver_level = request.form.get("destinataire")
    if receiver_level == None:
      flash("Veuillez choisir un destinataire !", category="error")
      return render_template("faire_un_don.jinja", engine=engine, player=player)
    amount = request.form.get("montant")
    if amount == "":
      flash("Veuiller indiquer un montant !", category="error")
      return render_template("faire_un_don.jinja", engine=engine, player=player)
    receiver_level = int(receiver_level)
    receiver = player.other_players[receiver_level]
    amount = int(amount)
    if amount <= 0:
      flash("Le montant à envoyer ne peut pas être negatif ou nul !", category="error")
      return render_template("faire_un_don.jinja", engine=engine, player=player)
    if amount > player.flouze:
      flash("Le montant indiqué dépasse votre solde !", category="error")
      return render_template("faire_un_don.jinja", engine=engine, player=player)
    player.send_money(receiver, amount)
    return redirect(url_for("views.home"))
  return render_template("faire_un_don.jinja", engine=engine, player=player)

@views.route("/partager_profit", methods=["GET", "POST"])
def partager_profit():
  player = engine.players[session["ID"]]
  if request.method == "POST":
    amounts = []
    for receiver in player.other_players:
      amount = request.form.get(receiver.name)
      amount = 0 if amount == "" else int(amount)
      if amount < 0:
        flash("Vous ne pouvez pas envoiyer des montants négatifs !", category="error")
        return render_template("partager.jinja", engine=engine, player=player)
      amounts.append(amount)
    if sum(amounts) > player.last_profit:
      flash("Vous ne pouvez pas donner plus que ce que vous avez reçu !", category="error")
      return render_template("partager.jinja", engine=engine, player=player)
    if sum(amounts) > player.last_profit:
      flash("Vous ne pouvez pas donner plus que ce que vous avez avez !", category="error")
      return render_template("partager.jinja", engine=engine, player=player)
    player.share_profit(amounts)
    return redirect(url_for("views.home"))
  return render_template("partager.jinja", engine=engine, player=player)

@views.route("/donner_des_etoiles", methods=("GET", "POST"))
def donner_etoiles():
  player = engine.players[session["ID"]]
  if request.method == "POST" and "don_etoiles" not in request.form:
    receiver_level = request.form.get("destinataire")
    amount = request.form.get("quantité")
    if receiver_level == None:
      flash("Veuiller choisir un destinataire !", category="error")
      return render_template("don_etoiles.jinja", engine=engine, player=player)
    if amount == "":
      flash("Veuiller indiquer un nombre d'étoiles !", category="error")
      return render_template("don_etoiles.jinja", engine=engine, player=player)
    receiver_level = int(receiver_level)
    amount = int(amount)
    if amount <= 0:
      flash("Le nombre d'étoiles à envoyer ne peut pas être negatif ou nul", category="error")
      return render_template("don_etoiles.jinja", engine=engine, player=player)
    if amount > player.stars:
      flash("Vous n'avez pas assez d'étoiles", category="error")
      return render_template("don_etoiles.jinja", engine=engine, player=player)
    receiver = player.other_players[receiver_level]
    player.send_stars(receiver, amount)
    return redirect(url_for("views.home"))
  return render_template("don_etoiles.jinja", engine=engine, player=player)
  

@views.route("/", methods=["GET", "POST"])
def home():
  player = engine.players[session["ID"]]
  game = engine.current_game
  if request.method == "POST":
    if "jeu1" in request.form:
      if not game.is_allowed_to_play(player, 1):
        return redirect(url_for("views.home"))
      tickets = request.form.get("tickets")
      if tickets == None:
        flash("Veuiller faire un choix !", category="error")
        return render_template(engine.current_page["url"], engine=engine, player=player)
      tickets = int(tickets)
      player.choice = tickets
      engine.log(f"{player.name} a choisis {tickets} tickets.")
      player.flash_message(f"Vous avez choisis {tickets} tickets.")
      player.is_done = True
      engine.save_data()

    elif "jeu2" in request.form:
      if not game.is_allowed_to_play(player, 2):
        return redirect(url_for("views.home"))
      if "choice" not in request.form:
        flash("Veuiller choisir un nombre !", category="error")
        return render_template(engine.current_page["url"], engine=engine, player=player)
      player.choice = int(request.form["choice"])
      engine.log(f"{player.name} a choisis le nombre {player.choice}.")
      player.flash_message(f"Vous avez choisis le nombre {player.choice}.")
      player.is_done = True
      engine.save_data()

    elif "jeu3" in request.form:
      if not game.is_allowed_to_play(player, 3):
        return redirect(url_for("views.home"))
      amount = request.form.get("montant")
      if amount == "":
        flash("Veuiller indiquer un montant !", category="error")
        return render_template(engine.current_page["url"], engine=engine, player=player)
      amount = int(amount)
      if amount < 0:
        flash("Le montant à investir ne peut pas être negatif !", category="error")
        return render_template(engine.current_page["url"], engine=engine, player=player)
      if amount > player.flouze:
        flash("Le montant indiqué dépasse votre solde !", category="error")
        return render_template(engine.current_page["url"], engine=engine, player=player)
      player.flouze -= amount
      player.choice = amount
      engine.log(f"{player.name} a versé {amount} Pièces dans le pot commun")
      player.flash_message(f"Vous avez versé {amount} {icons['coin']} dans le pot commun")
      player.is_done = True
      engine.save_data()
        
    elif "jeu4" in request.form:
      if not game.is_allowed_to_play(player, 4):
        return redirect(url_for("views.home"))
      if "choice" not in request.form:
        flash("Veuiller choisir un prix !", category="error")
        return render_template(engine.current_page["url"], engine=engine, player=player)
      player.choice = int(request.form["choice"])
      prizes = game.current_prizes
      prize = prizes[player.choice]
      if prize == "star":
        engine.log(f"{player.name} a choisis l'etoile.")
        player.flash_message(f"Vous avez choisis le prix : {icons['star']}")
      else:
        engine.log(f"{player.name} a choisis le prix : {prize} Pièces")
        player.flash_message(f"Vous avez choisis le prix : {prize} {icons['coin']}")
      player.is_done = True
      engine.save_data()
    
    elif "don_etoiles" in request.form:
      assert request.form["don_etoiles"] == "terminer"
      player.is_done = True
      engine.save_data()

    elif "jeu5" in request.form:
      assert request.form["jeu5"] in ["proposition", "nouvelle_proposition", "refuser", "accepter", "quiz_reponse"]
      
      if request.form["jeu5"] == "quiz_reponse":
        answer = request.form.get("réponse")
        engine.log(f'{player.name} a donner la réponse {answer} au quiz')
        game.current_answer = answer
      
      elif request.form["jeu5"] == "proposition":
        if not game.is_allowed_to_play(player, 5):
          return redirect(url_for("views.home"))
        total = 0
        for other_player in game.other_players:
          amount = request.form.get(other_player.name)
          if amount == "":
            flash("Veuiller indiquer un montant pour tous les joueurs !", category="error")
            return render_template("Jeu5-proposition.jinja", engine=engine, player=player)
          amount = int(amount)
          total += amount
        if total > player.flouze:
          flash("Les propositions que vous avez faites dépasse vos moyens !", category="error")
          return render_template("Jeu5-proposition.jinja", engine=engine, player=player)
        for i, other_player in enumerate(game.other_players):
          amount = int(request.form.get(other_player.name))
          amount = int(amount)
          game.current_proposition[i] = amount
          other_player.message = f"{player.name} vous fait une proposition de {amount} {icons['coin']}"
        player.is_done = True
        engine.next_page()
        engine.save_data()
      
      elif request.form["jeu5"] in ["refuser", "accepter"]:
        if not game.is_allowed_to_play(player, 5):
          return redirect(url_for("views.home"))
        player.choice = request.form["jeu5"] == "accepter"
        player.is_done = True
        engine.save_data()
      
      elif request.form["jeu5"] == "nouvelle_proposition":
        engine.next_page()
        engine.save_data()

  if engine.current_page["url"] == "Jeu 5":
    if engine.current_page["phase"] == "proposition":
      if player == game.master:
        return render_template("Jeu5-proposition.jinja", engine=engine, player=player)
      elif game.current_round_id == 0 and game.question_id < 3:
        if player == game.current_guesser:
          return render_template("quiz.jinja", engine=engine, player=player, input=True)
        else:
          return render_template("quiz.jinja", engine=engine, player=player, input=False)
      else:
        return render_template("results.jinja", engine=engine, player=player)
    
    elif engine.current_page["phase"] == "validation":
      if player.is_done:
        return render_template("en_attente_jeu5.jinja", engine=engine, player=player)
      return render_template("Jeu5-Valider.jinja", engine=engine, player=player)
    
    elif engine.current_page["phase"] == "reveal":
      if player == game.master:
        return render_template("Jeu5-reveal.jinja", engine=engine, player=player)
      else:
        return render_template("results.jinja", engine=engine, player=player)

  if ("choix" in engine.current_page["url"]  or engine.current_page["url"] == "donner_des_etoiles.jinja") and player.is_done:
    return render_template("en_attente.jinja", engine=engine, player=player)

  return render_template(engine.current_page['url'], engine=engine, player=player)
