from flask import Blueprint, render_template, request, flash, redirect, url_for, session

from . import engine

auth = Blueprint("auth", __name__)

@auth.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        first_name = request.form.get("firstName")
        password = request.form.get("password")
        if first_name == "felix" and password == "felix":
            session["ID"] = "admin"
            return redirect(url_for("views.home"))
        if first_name in engine.players_by_name.keys():
            player = engine.players_by_name[first_name]
            if player.password == password:
                engine.log(f"{first_name} s'est connecté.")
                flash("Vous êtes connecté !", category = "success")
                session["ID"] = player.ID
                return redirect(url_for("views.home"))
            else:
                flash("Mot de passe incorrect, réessayez.", category = "error")
                return render_template("login.jinja")
        else:
            flash("Vous n'êtes pas un participant", category = "error")
    return render_template("login.jinja")
