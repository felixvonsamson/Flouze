from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from . import players


auth = Blueprint('auth', __name__)


@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        password = request.form.get('password')
        if first_name == "felix" and password == "felix":
            session["user"] = "admin"
            return redirect(url_for('views.home'))
        for i in range(5):
            if first_name == players[i]["name"]:
                if players[i]["password"] == password:
                    flash('Logged in successfully!', category = 'success')
                    session["user"] = players[i]
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again.', category = 'error')
                    return render_template("login.html")
        flash('You are not a participant', category = 'error')
    return render_template("login.html")
