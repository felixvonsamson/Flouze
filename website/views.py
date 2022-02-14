from flask import Blueprint, render_template, request, flash, session, redirect, url_for, Markup
from . import pages, iterator, players, socketio, done, prizes
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
    global iterator
    global done
    if "ID" not in session :
        return redirect(url_for('auth.login'))
    if session["ID"] == "admin":
        if request.method == 'POST':

           if request.form['boutton'] == 'page suivante' and iterator < len(pages)-1:
               iterator += 1
               for i in players:
                   i["done"] = False
                   i["choix"] = None
               done = 0
               update_data()

           if request.form['boutton'] == 'page précedente' and iterator > 0:
               iterator -= 1
               update_data()

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

        if request.form['boutton'] == "envoyer don":
            destinataire = request.form.get('destinataire')
            montant = request.form.get('montant')
            if destinataire == None:
                flash('Veuiller choisir un destinataire', category='error')
                return render_template("faire_un_don.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            if montant == '':
                flash('Veuiller indiquer un montant', category='error')
                return render_template("faire_un_don.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            destinataire = int(destinataire)
            montant = int(montant)
            if montant < 1:
                flash('Le montant à envoyer ne peut pas être negatif ou nul', category='error')
                return render_template("faire_un_don.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            if montant > players[session["ID"]]["flouze"]:
                flash('Le montant indiqué dépasse votre solde', category='error')
                return render_template("faire_un_don.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            players[session["ID"]]["flouze"] -= montant
            players[otherPlayers[destinataire]["ID"]]["flouze"] += montant
            flash(Markup('Vous avez envoyé ' + str(montant) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin"> à ' + otherPlayers[destinataire]["name"]), category='success')
            update_data()
            return render_template(pages[iterator], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)

        if request.form['boutton'] == "jeu1-choix":
            tickets = request.form.get('tickets')
            if tickets == None:
                flash('Veuiller faire un choix', category='error')
                return render_template(pages[iterator], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            players[session["ID"]]["choix"] = int(tickets)
            players[session["ID"]]["done"] = True
            done += 1
            flash('Vous avez choisis ' + tickets + ' tickets', category='success')
            if done == 5:
                lottery = []
                for i in players:
                    for j in range(i["choix"]):
                        lottery.append(i["ID"])
                    i["message"] = Markup("Vous n'avez pas gagné la lotterie <i class='fa fa-frown-o'></i>")
                if len(lottery) > 0:
                    winner = lottery[random.randint(0,len(lottery)-1)]
                    prize = round(prizes[iterator]/len(lottery))
                    players[winner]["flouze"] += prize
                    players[winner]["message"] = Markup("Vous avez gagné la lotterie ! <br> Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" style="width:25px" alt="Coin">')
            update_data()

        if pages[iterator] == "Jeu2-choix.html":
            if request.form['boutton'] == '1':
                players[session["ID"]]["choix"] = 1
            if request.form['boutton'] == '2':
                players[session["ID"]]["choix"] = 2
            if request.form['boutton'] == '3':
                players[session["ID"]]["choix"] = 3
            if request.form['boutton'] == '4':
                players[session["ID"]]["choix"] = 4
            if request.form['boutton'] == '5':
                players[session["ID"]]["choix"] = 5
            if request.form['boutton'] == "validate num":
                if players[session["ID"]]["choix"] == None:
                    flash('Veuiller choisir un nombre', category='error')
                    return render_template(pages[iterator], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
                players[session["ID"]]["done"] = True
                done += 1
                flash('Vous avez choisis le nombre ' + str(players[session["ID"]]["choix"]), category='success')
                if done == 5:
                    iterator += 1
                    for i in players:
                        i["done"] = False
                    done = 0
                update_data()


    if done == 5:
        return render_template("results.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
    if players[session["ID"]]["done"]:
        return render_template("en_attente.html", done=done, user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
    return render_template(pages[iterator], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
