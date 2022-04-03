from unicodedata import category
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
  if request.method == "POST":
    game = engine.current_game
    if "reveal" in request.form:
      assert request.form["reveal"] in map(str, range(5))
      game.reveal_card(int(request.form["reveal"]))

    elif "diapo" in request.form:
      assert request.form["diapo"] in ["precedant", "suivant"]
      if request.form["diapo"] == "suivant":
        game.next_frame()
      elif request.form["diapo"] == "precedant":
        game.previous_frame()

    elif "page" in request.form:
      assert request.form["page"] in ["precedant", "suivant", "suivant_passif"]
      if request.form["page"] == "precedant" and engine.iterator:
        engine.passive_previous_page()
      elif request.form["page"] == "suivant" \
        and engine.iterator < len(engine.pages) - 1:
        if engine.current_page["url"] == "results.jinja":
          for player in engine.players:
            player.last_profit = 0
            player.flouze_request = None
        engine.next_page()
      elif request.form["page"] == "suivant_passif" and engine.iterator:
        engine.passive_next_page()
        
    elif "quiz" in request.form:
      decision = request.form["quiz"][:-1]
      question_id = request.form["quiz"][-1:]
      assert decision in ["rejeter", "valider"]
      assert question_id in map(str, range(4))
      question_id = int(question_id)
      question, correct_answer = game.quiz[question_id][1]
      if decision == "rejeter":
        game.is_answer_correct[question_id] = False
        for player in game.other_players:
          player.send_message(
            f'Perdu ! La bonne réponse à la question "{question}" était : '\
            f'{correct_answer}', category="error")
      elif decision == "valider":
        game.is_answer_correct[question_id] = True
        for player in game.other_players:
          quiz_prize = game.config["quiz_prize"]
          player.flouze += quiz_prize
          updates = [("flouze", player.flouze)]
          player.engine.update_fields(updates, [player])
          player.send_message(
            f"Félicitation ! Vous remportez {quiz_prize} {icons['coin']} !")
        
    elif "current_page_id" in request.form:
      engine.goto_page(int(request.form["current_page_id"]))
      
    engine.save_data()
  
  return render_template("monitoring.jinja", engine=engine)
