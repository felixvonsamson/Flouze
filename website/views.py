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
        engine.iterator -= 1
        engine.log(f"Retour à la page précedente : {engine.current_page['url']} (jeu {engine.current_stage[0]}, manche {engine.current_stage[1]})")
        engine.save_data()
        engine.force_refresh()

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
      player.is_done = True
      engine.save_data()
    
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
      player.flash_message(f"Vous avez choisis {tickets} tickets.")
      engine.save_data()
    if engine.current_page["url"] == "Jeu2-choix.jinja":
      #action = check_action_allowed(player, 2)
      #if action: return action
      if request.form["boutton"] == "validate num":
        if "choice" not in request.form:
          flash("Veuiller choisir un nombre !", category="error")
          return render_template(engine.current_page["url"], engine=engine, player=player)
        player.choice = int(request.form["choice"])
        engine.log(f"{player.name} a choisis le nombre {player.choice}.")
        player.is_done = True
        player.flash_message(f"Vous avez choisis le nombre {player.choice}.")
        engine.save_data()

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
      player.flash_message(f"Vous avez versé {amount} {icons['coin']} dans le pot commun")
      engine.save_data()

    if engine.current_page["url"] == "Jeu4-choix.jinja":
      #action = check_action_allowed(player, 4)
      #if action: return action
      if request.form["boutton"] == "Jeu4-choix":
        if "choice" not in request.form:
          flash("Veuiller choisir un prix !", category="error")
          return render_template(engine.current_page["url"], engine=engine, player=player)
        player.choice = int(request.form["choice"])
        player.is_done = True
        prizes = game.current_prizes
        prize = prizes[player.choice]
        if prize == "star":
          engine.log(f"{player.name} a choisis l'etoile.")
          player.flash_message(f"Vous avez choisis le prix : {icons['star']}")
        else:
          engine.log(f"{player.name} a choisis le prix : {prize} Pièces")
          player.flash_message(f"Vous avez choisis le prix : {prize} {icons['coin']}")
        engine.save_data()





    if request.form["boutton"] == "retour don etoiles":
      return render_template(engine.current_page['url'], player=player, engine=engine)

    if engine.current_page['url'] == "Jeu 5":
      if request.form["boutton"] == 'quiz':
        answer = request.form.get("réponse")
        engine.log(f'{player.name} a donner la réponse {answer} au quiz')


      if request.form["boutton"] == 'proposition':
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
          other_player.message = Markup(f"{player.name} vous fait une proposition de {amount} {icons['coin']}")
        player.is_done = True
        engine.next_page()


      elif request.form["boutton"] in ["0", "1"]:
        if player.is_done: pass
        player.choice = int(request.form["boutton"])
        player.is_done = True
      elif request.form["boutton"] == 'nouvelle proposition':
        engine.next_page()
      engine.save_data()

  if engine.current_page['url'] == "Jeu 5":
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

  return render_template(engine.current_page['url'], player=player, engine=engine)
