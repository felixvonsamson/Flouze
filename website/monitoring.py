from flask import request, session
from flask import render_template, redirect, url_for
from flask import Blueprint
from website import engine

from .html_icons import icons

monitoring = Blueprint("monitoring", __name__)

@monitoring.route("/monitoring", methods=("GET", "POST"))
def home():
  if session["ID"] != "admin":
    return redirect(url_for("views.home"))
  
  game = engine.current_game

  if "reveal" in request.form:
    assert request.form["reveal"] in map(str, range(5))
    game.reveal_card(int(request.form["reveal"]))

  elif "diapo" in request.form:
    assert request.form["diapo"] in ["precedant", "suivant"]
    if request.form["diapo"] == "suivant":
      game.next_frame()
    elif request.form["diapo"] == "précedant":
      game.previous_frame()

  elif "page" in request.form:
    assert request.form["page"] in ["precedant", "suivant"]
    if request.form["page"] == "suivant" \
       and engine.iterator < len(engine.pages) - 1:
      if engine.current_page["url"] == "results.jinja":
        for player in engine.players:
          player.last_profit = 0
      engine.next_page()
      engine.save_data()

    elif request.form["page"] == "precedant" and engine.iterator:
      engine.passive_previous_page()
      engine.save_data()
      
  elif "quiz" in request.form:
    assert request.form["quiz"] in ["rejeter", "valider"]
    if request.form["quiz"] == "rejeter":
      for player in game.other_players:
        player.send_message(
          f"Perdu ! La bonne réponse était : {game.current_question[1][1]}")
    elif request.form["quiz"] == "valider":
      for player in game.other_players:
        quiz_prize = game.config['quiz_prize']
        player.flouze += quiz_prize
        player.send_message(
          f"Félicitation ! Vous remportez {quiz_prize} {icons['coin']} !")
    engine.force_refresh()
    engine.save_data()
      
  return render_template("monitoring.jinja", engine=engine)
