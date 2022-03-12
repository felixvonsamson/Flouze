from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from . import players, log
import datetime


auth = Blueprint('auth', __name__)


@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        password = request.form.get('password')
        if first_name == "felix" and password == "felix":
            session["ID"] = "admin"
            return redirect(url_for('views.home'))
        for i in range(5):
            if first_name == players[i]["name"]:
                if players[i]["password"] == password:
                    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + first_name + " s'est connecté")
                    flash('Vous êtes connecté !', category = 'success')
                    session["ID"] = i
                    return redirect(url_for('views.home'))
                else:
                    flash('Mot de passe incorrect, réessayez.', category = 'error')
                    return render_template("login.html")
        flash("Vous n'êtes pas un participant", category = 'error')
    return render_template("login.html")
