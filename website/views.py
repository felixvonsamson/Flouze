from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from . import pages, iterator, players
import random

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if "user" not in session :
        return redirect(url_for('auth.login'))
    current_user = session["user"]
    if current_user == "admin":
        #if request.method == 'POST':
        #    return
        #    if request.form['boutton'] == 'increment':
        #        iterator += 1
        print(iterator)
        return render_template("monitoring.html" , players=players, pages=pages, iterator=iterator)

    otherPlayers = players
    otherPlayers.pop(current_user["ID"])
    if request.method == 'POST':

        if request.form['boutton'] == 'increment':
            current_user.["flouze"] = random.randint(0,100000)
            current_user.["stars"] += 1

        if request.form['boutton'] == 'don':
            return render_template("faire_un_don.html", user=current_user , playerIDs=otherID, players=players)

        if request.form['boutton'] == "jeu1-choix":
            tickets = request.form.get('tickets')
            if tickets==None :
                flash('Veuiller faire un choix', category='error')
                return render_template(pages[iterator], user=current_user , playerIDs=otherID, players=players)
            flash('Vous avez choisis '+tickets+' tickets', category='success')

    return render_template(pages[iterator], user=current_user , playerIDs=otherID, players=players)
