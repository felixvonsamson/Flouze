from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from . import pages, iterator, players, socketio
import random
import pickle
from flask_socketio import send, emit

views = Blueprint('views', __name__)

def update_data():
    with open("data.pck", 'wb') as file:
        pickle.dump((iterator, players), file)
    socketio.emit('changed', None, broadcast=True)

@views.route('/', methods=['GET', 'POST'])
def home():
    if "ID" not in session :
        return redirect(url_for('auth.login'))
    if session["ID"] == "admin":
        if request.method == 'POST':
           if request.form['boutton'] == 'increment':
               global iterator
               iterator += 1
               update_data()
        print(iterator)
        return render_template("monitoring.html" , players=players, pages=pages, iterator=iterator)
    otherPlayers = players.copy()
    otherPlayers.pop(session["ID"])
    if request.method == 'POST':

        if request.form['boutton'] == 'increment':
            players[session["ID"]]["flouze"] = random.randint(0,100000)
            players[session["ID"]]["stars"] += 1
            update_data()

        if request.form['boutton'] == 'don':
            return render_template("faire_un_don.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)

        if request.form['boutton'] == "jeu1-choix":
            tickets = request.form.get('tickets')
            if tickets==None :
                flash('Veuiller faire un choix', category='error')
                return render_template(pages[iterator], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            flash('Vous avez choisis '+tickets+' tickets', category='success')

    return render_template(pages[iterator], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
