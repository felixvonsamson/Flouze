from flask import current_app, request, session, g
from flask import render_template, redirect, url_for, flash
from flask import Blueprint

from .html_icons import icons

views = Blueprint("views", __name__)
flash_error = lambda msg: flash(msg, category="error")

@views.before_request
def check_user():
  if session["ID"] == "admin":
    return redirect(url_for("monitoring.home"))
  assert session["ID"] in range(5)
  g.engine = current_app.config["engine"]
  g.player = g.engine.players[session["ID"]]
  def render_template_ctx(page):
    g.player.last_page = page
    return render_template(page, engine=g.engine, player=g.player)
  g.render_template_ctx = render_template_ctx


@views.route("/faire_un_don", methods=("GET", "POST"))
def donner_flouze():
  if request.method == "POST":
    if not g.engine.use_nonce(request.form.get("envoyer")):
      return redirect(url_for("views.home"))
    receiver_level = int(request.form.get("destinataire"))
    amount = int(request.form.get("montant"))
    receiver = g.player.other_players[receiver_level]
    if amount > g.player.flouze:
      flash_error(g.engine.text["player_txt"]["not enough money"]\
        [g.player.lang_id])
      return g.render_template_ctx("faire_un_don.jinja")
    g.player.send_money(receiver, amount)
    return redirect(url_for("views.home"))
  g.engine.refresh_monitoring()
  return g.render_template_ctx("faire_un_don.jinja")

@views.route("/partager_profit", methods=["GET", "POST"])
def partager_profit():
  if request.method == "POST":
    if not g.engine.use_nonce(request.form.get("envoyer")) \
       or g.player.last_profit is None:
      return redirect(url_for("views.home"))
    amounts = []
    if g.player.last_profit < 0 : 
      for receiver in g.player.other_players:
        amount = int(request.form.get(receiver.name))
        if amount > 0:
          flash_error(g.engine.text["player_txt"]["please use donation"]\
            [g.player.lang_id])
          return g.render_template_ctx("partager.jinja")
        amounts.append(amount)
      if sum(amounts) < g.player.last_profit:
        flash_error(g.engine.text["player_txt"]["claim too high"]\
          [g.player.lang_id])
        return g.render_template_ctx("partager.jinja")
    else:
      for receiver in g.player.other_players:
        amount = int(request.form.get(receiver.name))
        amounts.append(amount)
      if sum(amounts) > g.player.last_profit:
        flash_error(g.engine.text["player_txt"]["donation too high"]\
          [g.player.lang_id])
        return g.render_template_ctx("partager.jinja")
      if sum(amounts) > g.player.flouze:
        flash_error(g.engine.text["player_txt"]\
          ["not enough money for donation"][g.player.lang_id])
        return g.render_template_ctx("partager.jinja")
    g.player.share_profit(amounts)
    return redirect(url_for("views.home"))
  g.engine.refresh_monitoring()
  return g.render_template_ctx("partager.jinja")

@views.route("/donner_des_etoiles", methods=("GET", "POST"))
def donner_etoiles():
  if request.method == "POST":
    if not g.engine.use_nonce(request.form.get("envoyer")):
      return redirect(url_for("views.home"))
    receiver_level = int(request.form.get("destinataire"))
    amount = int(request.form.get("quantité"))
    if amount > g.player.stars:
      flash_error(g.engine.text["player_txt"]["not enough stars"]\
        [g.player.lang_id])
      return g.render_template_ctx("don_etoiles.jinja")
    receiver = g.player.other_players[receiver_level]
    g.player.send_stars(receiver, amount)
    return redirect(url_for("views.home"))
  return g.render_template_ctx("don_etoiles.jinja")
  

@views.route("/", methods=["GET", "POST"])
def home():
  game = g.engine.current_game
  if request.method == "POST":

    if "jeu1" in request.form:
      if not game.is_allowed_to_play(g.player, 1):
        return redirect(url_for("views.home"))
      tickets = int(request.form.get("tickets"))
      g.player.choice = tickets
      
    elif "jeu2" in request.form:
      if not game.is_allowed_to_play(g.player, 2):
        return redirect(url_for("views.home"))
      g.player.choice = int(request.form["choice"])

    elif "jeu3" in request.form:
      if not game.is_allowed_to_play(g.player, 3):
        return redirect(url_for("views.home"))
      amount = int(request.form.get("montant"))
      if amount > g.player.flouze:
        flash_error(g.engine.text["player_txt"]["not enough money"]\
          [g.player.lang_id])
        return g.render_template_ctx(g.engine.current_page["url"])
      g.player.choice = amount
        
    elif "jeu4" in request.form:
      if not game.is_allowed_to_play(g.player, 4):
        return redirect(url_for("views.home"))
      g.player.choice = int(request.form["choice"])
    
    elif "don_etoiles" in request.form:
      assert request.form["don_etoiles"] == "terminer"
      g.player.is_done = True

    elif "jeu5" in request.form:
      assert request.form["jeu5"] in [
        "proposition", "nouvelle_proposition", 
        "refusé", "accepté", "quiz_reponse"]
      
      if request.form["jeu5"] == "quiz_reponse":
        game.current_answer = request.form.get("réponse")
      
      elif request.form["jeu5"] == "proposition":
        if not game.is_allowed_to_play(g.player, 5):
          return redirect(url_for("views.home"))
        total = 0
        for other_player in game.other_players:
          amount = int(request.form.get(other_player.name))
          if amount + other_player.flouze < 0:
            flash_error(g.engine.text["player_txt"]["claim can't be accepted"]\
              [g.player.lang_id].format(name = other_player.name))
            return g.render_template_ctx("Jeu5-proposition.jinja")
          total += amount
        if total > g.player.flouze:
          flash_error(g.engine.text["player_txt"]["not enough money for offer"]\
            [g.player.lang_id])
          return g.render_template_ctx("Jeu5-proposition.jinja")
        amounts = [int(request.form.get(other_player.name)) 
                   for other_player in game.other_players]
        game.make_proposition(amounts)
      
      elif request.form["jeu5"] in ["declined", "accepted"]:
        if not game.is_allowed_to_play(g.player, 5):
          return redirect(url_for("views.home"))
        g.player.choice = request.form["jeu5"]
      
      elif request.form["jeu5"] == "nouvelle_proposition":
        g.engine.next_page(refresh=False)
        g.engine.save_data()

  if g.player.is_sharing_money:
    g.engine.refresh_monitoring()
  
  if g.engine.current_page["url"] == "Jeu 5":
    if g.engine.current_page["phase"] == "proposition":
      if g.player == game.master:
        return g.render_template_ctx("Jeu5-proposition.jinja")
      elif game.current_round_id == 0 and game.question_id < 4:
        return g.render_template_ctx("quiz.jinja")
      else:
        return g.render_template_ctx("results.jinja")
    
    elif g.engine.current_page["phase"] == "validation":
      if g.player.is_done:
        return g.render_template_ctx("en_attente_jeu5.jinja")
      return g.render_template_ctx("Jeu5-Valider.jinja")
    
    elif g.engine.current_page["phase"] == "reveal":
      if g.player == game.master:
        return g.render_template_ctx("Jeu5-reveal.jinja")
      else:
        return g.render_template_ctx("results.jinja")

  if "choix" in g.engine.current_page["url"] and g.player.is_done:
    return g.render_template_ctx("en_attente.jinja")
  
  return g.render_template_ctx(g.engine.current_page["url"])
