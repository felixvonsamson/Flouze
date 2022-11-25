from flask import current_app, request, session
from flask import render_template, redirect, url_for, flash
from flask import Blueprint

from .text import player_txt, log_txt

auth = Blueprint("auth", __name__)

@auth.route("/login", methods = ["GET", "POST"])
def login():
  engine = current_app.config["engine"]
  if request.method == "POST":
    first_name = request.form.get("firstName")
    password = request.form.get("password")
    if first_name == "felix" and password == "felix":
      session["ID"] = "admin"
      return redirect(url_for("monitoring.home"))
    if first_name in engine.players_by_name.keys():
      player = engine.players_by_name[first_name]
      if player.password == password:
        engine.log(log_txt["connected"][engine.lang_id].format(name=first_name))
        player.flash_message(player_txt["connected"][player.lang_id])
        session["ID"] = player.ID
        engine.save_data()
        engine.refresh_monitoring()
        return redirect(url_for("views.home"))
      else:
        flash(player_txt["incorect password"][engine.lang.id], category = "error")
        return render_template("login.jinja")
    else:
      flash(player_txt["not recognized"][engine.lang.id], category = "error")
  return render_template("login.jinja")
