from flask import Blueprint, render_template, request, session, redirect, url_for
from website import engine

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
    if request.form["page"] == "suivant" and engine.iterator < len(engine.pages)-1:
      if engine.current_page["url"] == "results.jinja":
        for player in engine.players:
          player.last_profit = 0
      engine.next_page()
      engine.save_data()
      engine.force_refresh()

    elif request.form["page"] == "precedant" and engine.iterator:
      engine.iterator -= 1
      engine.log(f"Retour à la page précedente : {engine.current_page['url']} (jeu {engine.current_stage[0]}, manche {engine.current_stage[1]})")
      engine.save_data()
      engine.force_refresh()
    
  return render_template("monitoring.jinja", engine=engine)
