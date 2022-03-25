from flask import Blueprint, render_template, request, flash, session, redirect, url_for, Markup, current_app 
from website import engine

from .html_icons import icons

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
def home():
  if "ID" not in session :
    return redirect(url_for("auth.login"))

  game = engine.current_game
  if session["ID"] == "admin":
    if request.method == "POST":
      assert "boutton" in request.form and request.form["boutton"] in ["page suivante", "page précedente"] or\
           "reveal" in request.form and request.form["reveal"] in map(str, range(5)) or\
           "diapo" in request.form and request.form["diapo"] in ["suivant", "précedent"]
      if "reveal" in request.form:
        game.reveal_card(int(request.form["reveal"]))
      elif "diapo" in request.form:
        if request.form["diapo"] == "suivant":
          game.next_frame()
        if request.form["diapo"] == "précedent":
          game.previous_frame()
      elif request.form["boutton"] == "page suivante" and engine.iterator < len(engine.pages)-1:
        if engine.current_page["url"] == "results.jinja":
          for player in engine.players:
            player.last_profit = None

        engine.next_page()
        engine.save_data()
        engine.force_refresh()

      elif request.form["boutton"] == "page précedente" and engine.iterator:
        game.next_frame()
        return render_template("monitoring.jinja", engine=engine, imax=min(len(engine.logs),20))

        for p in players:
          p["choix"] = False
          p["done"] = False
        gameState["done"] = 0
        engine.iterator -= 1
        engine.log(f"Retour à la page précedente : {engine.current_page['url']} (jeu {engine.current_stage[0]}, manche {engine.current_stage[1]})")
        save_data()
        force_refresh()

    return render_template("monitoring.jinja", engine=engine, imax=min(len(engine.logs),20))
  
  assert session["ID"] in range(5)
  player = engine.players[session["ID"]]
  if request.method == "GET":
    pass
  if request.method == "POST":
    if request.form["boutton"] == "partager":
      return render_template("partager.jinja", engine=engine, player=player)

    if request.form["boutton"] == "don":
      return render_template("faire_un_don.jinja", engine=engine, player=player)

    if request.form["boutton"] == "léguer etoiles":
      return render_template("don_etoiles.jinja", engine=engine, player=player)

    if request.form["boutton"] == "en fait non":
        return render_template(engine.current_page["url"], engine=engine, player=player)
    
    if request.form["boutton"] == "envoyer don":
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
      return render_template(engine.current_page["url"], engine=engine, player=player)

    if request.form["boutton"] == "envoi partager":
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
      return render_template(engine.current_page["url"], engine=engine, player=player)

    if request.form["boutton"] == "envoyer etoile":
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
      return render_template("don_etoiles.jinja", engine=engine, player=player)

    if request.form["boutton"] == "jeu1-choix":
      #action = check_action_allowed(player, 1)
      #if action: return action
      tickets = request.form.get("tickets")
      if tickets == None:
        flash("Veuiller faire un choix !", category="error")
        return render_template(engine.current_page["url"], engine=engine, player=player)
      player.choice = int(tickets)
      engine.log(f"{player.name} a choisis {tickets} tickets.")
      player.is_done = True
      flash(f"Vous avez choisis {tickets} tickets.", category="success")
      engine.save_data()

    if engine.current_page["url"] == "Jeu2-choix.jinja":
      #action = check_action_allowed(player, 2)
      #if action: return action
      if request.form["boutton"] == "validate num":
        if player.choice == None:
          flash("Veuiller choisir un nombre !", category="error")
          return render_template(engine.current_page["url"], engine=engine, player=player)
        engine.log(f"{player.name} a choisis le nombre {player.choice}.")
        player.is_done = True
        flash(f"Vous avez choisis le nombre {player.choice}.", category="success")
        engine.save_data()
      else:
        player.choice = int(request.form["boutton"])
        engine.refresh_monitoring()

    if request.form["boutton"] == "Jeu3-choix":
      #action = check_action_allowed(player, 3)
      #if action: return action
      amount = request.form.get("montant")
      if amount == "":
        flash(Markup("Veuiller indiquer un montant<br>(0 si vous ne voulez rien investir) !"), category="error")
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
      player.is_done = True
      engine.log(f"{player.name} a versé {amount} Pièces dans le pot commun")
      flash(Markup(f"Vous avez versé {amount} {icons['coin']} dans le pot commun"), category="success")
      engine.save_data()

    if engine.current_page["url"] == "Jeu4-choix.jinja":
      #action = check_action_allowed(player, 4)
      #if action: return action
      if request.form["boutton"] == "Jeu4-choix":
        if player.choice == None:
          flash("Veuiller choisir un nombre !", category="error")
          return render_template(engine.current_page["url"], engine=engine, player=player)
        player.is_done = True
        prizes = game.config["prize"][game.bonuses]
        prize = prizes[player.choice]
        if prize[player.choice] == "star":
          engine.log(f"{player.name} a choisis l'etoile.")
          flash(Markup(f"Vous avez choisis le prix : {icons['star']}"), category="success")
        else:
          engine.log(f"{player.name} a choisis le prix : {prize} Pièces")
          flash(Markup(f"Vous avez choisis le prix : {prize} {icons['coin']}"), category="success")
        engine.save_data()
      else:
        player.choice = int(request.form["boutton"])





    if request.form["boutton"] == "terminer":
      game.is_done_stars[player.ID] = True
      if all(game.is_done_stars[player.ID]):
        engine.next_page()
      engine.save_data()

    if engine.current_page['url'] == "Jeu 5":
      if request.form["boutton"] == 'quiz':
        answer = request.form.get("réponse")
        engine.log(f'{player.name} a donner la réponse {answer} au quiz')


      if request.form["boutton"] == 'proposition':
        total = 0
        for player in game.other_players:
          amount = request.form.get(player.name)
          if amount == "":
            flash("Veuiller indiquer un montant pour tous les joueurs !", category="error")
            return render_template("Jeu5-proposition.jinja", player=player)
          amount = int(amount)
          total += amount
        if total > player.flouze:
          flash("Les propositions que vous avez faites dépasse vos moyens !", category="error")
          return render_template("Jeu5-proposition.jinja", player=player)
        for i, player in enumerate(game.other_players):
          amount = int(request.form.get(player.name))
          amount = int(amount)
          game.current_proposition[i] = amount
          player.message = Markup(f"{player.name} vous fait une proposition de {amount} {icons['coin']}")

        engine.next_page()


      elif request.form["boutton"] in ["0", "1"]:
        if player.is_done: pass
        player.choice = int(request.form["boutton"])
        player.is_done = True
      elif request.form["boutton"] == 'nouvelle proposition':
        engine.next_page()
      engine.save_data()

  if engine.current_page['url'] == "Jeu 5":
    if player.is_done:
      return render_template("en_attente_jeu5.jinja", player=player)

    if engine.current_page["phase"] == "proposition":
      if player == game.master:
        return render_template("Jeu5-proposition.jinja", player=player)
      elif game.current_round_id == 0 and game.question_id < 4:
        if player == game.current_guesser:
          return render_template("quiz.jinja", player=player, input=True)
        else:
          return render_template("quiz.jinja", player=player, input=False)
      else:
        return render_template("results.jinja", player=player)
    elif engine.current_page["phase"] == "validation":
      if player == game.master:
        return render_template("en_attente_jeu5.jinja", player=player)
      else:
        return render_template("Jeu5-Valider.jinja", player=player)
    elif engine.current_page["phase"] == "reveal":
      if player == game.master:
        return render_template("Jeu5-reveal.jinja", player=player)
      else:
        return render_template("results.jinja", player=player)

  if "choix" in engine.current_page["url"] and player.is_done:
    return render_template("en_attente.jinja", engine=engine, player=player)

  return render_template(engine.current_page['url'], player=player, engine=engine)
