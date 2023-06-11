from flask import current_app, request, session
from flask import render_template, redirect, url_for
from flask import Blueprint

from .html_icons import icons

monitoring = Blueprint("monitoring", __name__)

@monitoring.route("/monitoring", methods=("GET", "POST"))
def home():
  engine = current_app.config["engine"]
  if session["ID"] != "admin":
    return redirect(url_for("views.home"))
  if request.method == "POST":
    game = engine.current_game if engine.players is not None else None
    if "reveal" in request.form:
      assert request.form["reveal"] in map(str, range(len(engine.players)))
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
      elif request.form["page"] == "suivant_passif":
        engine.passive_next_page()
        
    elif "quiz" in request.form:
      decision = request.form["quiz"][:-1]
      question_id = request.form["quiz"][-1:]
      assert decision in ["refuse", "validate"]
      assert question_id in map(str, range(8))
      question_id = int(question_id)
      question, correct_answer = engine.text["quiz"][question_id]\
        [engine.lang_id]
      if decision == "refuse":
        game.is_answer_correct[question_id] = False
        engine.log(engine.text["logs_txt"]["awnser refused"][engine.lang_id])
        for player in game.other_players:
          player.send_message(engine.text["player_txt"]["wrong awnser"]\
            [player.lang_id].format(question = question,
            correct_answer = correct_answer), category="error")
      elif decision == "validate":
        game.is_answer_correct[question_id] = True
        engine.log(engine.text["logs_txt"]["awnser accepted"][engine.lang_id])
        
    elif "current_page_id" in request.form:
      engine.goto_page(int(request.form["current_page_id"]))

    elif "player1" in request.form:
      players = []
      for p_id in range(8):
        name = request.form[f"player{p_id+1}"]
        if name == "":
          break
        players.append(name)
      engine.init_players_raw(list(enumerate(players)))

    engine.save_data()
  
  if engine.current_page["url"] == "final-results.jinja":
    return render_template("monitoring-recap.jinja", engine=engine)
  else:
    if engine.players is None:
      return render_template("game_config.jinja", engine=engine)
    else:
      return render_template("monitoring.jinja", engine=engine)