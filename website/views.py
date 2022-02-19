from flask import Blueprint, render_template, request, flash, session, redirect, url_for, Markup
from . import pages, iterator, players, socketio, done, bonus_jeu4
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
    global bonus_jeu4
    if "ID" not in session :
        return redirect(url_for('auth.login'))
    if session["ID"] == "admin":
        if request.method == 'POST':

           if request.form['boutton'] == 'page suivante' and iterator < len(pages)-1:



               if pages[iterator]['url'] == "Jeu2-reveal.html":
                   for p in players:
                       p["message"] = "Personne n'a remporté de lot a cette manche"
                   for i in range(1, 6):
                       count = 0
                       player = None
                       for p in players:
                           if p["choix"] == i:
                               count += 1
                               player = p
                       if count == 1:
                           prize = pages[iterator]["prize"]*i
                           player["flouze"] += prize
                           for p in players:
                               p["message"] = Markup(player["name"] + " a gagné et a remporté " + str(prize) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin">')
                           break

               if pages[iterator]['url'] == "Jeu4-reveal.html":
                   for p in players:
                       p["message"] = "Vous n'avez pas remporter le prix"
                   bonus = 0
                   for i in range(5):
                       count = 0
                       player = None
                       for p in players:
                           if p["choix"] == i:
                               count += 1
                               player = p
                       if count == 1:
                           bonus += 1
                           if bonus_jeu4 == 0:
                               prize = pages[iterator]['prize'][i]
                           elif bonus_jeu4 == 1:
                               prize = pages[iterator]['prizeBonus'][i]
                           else:
                               prize = pages[iterator]['prizeDoubleBonus'][i]
                           if prize == "star":
                               player["stars"] += 1
                               player["message"] = Markup('Vous avez remporté le prix : <i class="fa fa-star"></i>')
                           else:
                               player["flouze"] += prize
                               player["message"] = Markup("Vous avez remporté le prix : " + str(prize) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin">')
                   if bonus == 5:
                       bonus_jeu4 += 1

               iterator += 1

               for i in players:
                   i["done"] = False
                   i["choix"] = None
               done = 0

               if pages[iterator]['url'] == "Jeu3-title.html":
                   for i in players:
                       i["saved_flouze"] = i["flouze"]
                       i["flouze"] = 1000

               if pages[iterator]['url'] == "Jeu4-title.html":
                   for i in players:
                       i["flouze"] += i["saved_flouze"]
                       i["saved_flouze"] = 0

               update_data()

           if request.form['boutton'] == 'page précedente' and iterator > 0:
               iterator -= 1
               update_data()

        return render_template("monitoring.html" , players=players, pages=pages, iterator=iterator, bonus=bonus_jeu4)
    otherPlayers = players.copy()
    otherPlayers.pop(session["ID"])
    if request.method == 'POST':

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
            return render_template(pages[iterator]['url'], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players, pages=pages)

        if request.form['boutton'] == "jeu1-choix":
            tickets = request.form.get('tickets')
            if tickets == None:
                flash('Veuiller faire un choix', category='error')
                return render_template(pages[iterator]['url'], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
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
                    prize = round(pages[iterator]["prize"]/len(lottery))
                    players[winner]["flouze"] += prize
                    players[winner]["message"] = Markup("Vous avez gagné la lotterie ! <br> Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" style="width:25px" alt="Coin">')
            update_data()

        if pages[iterator]['url'] == "Jeu2-choix.html":
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
                    return render_template(pages[iterator]['url'], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
                players[session["ID"]]["done"] = True
                done += 1
                flash('Vous avez choisis le nombre ' + str(players[session["ID"]]["choix"]), category='success')
                if done == 5:
                    iterator += 1
                    for p in players:
                        p["done"] = False
                    done = 0
                update_data()

        if request.form['boutton'] == "Jeu3-choix":
            montant = request.form.get('montant')
            if montant == '':
                flash(Markup('Veuiller indiquer un montant<br>(0 si vous ne voulez rien investir)'), category='error')
                return render_template(pages[iterator]['url'], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            montant = int(montant)
            if montant < 0:
                flash('Le montant à investir ne peut pas être negatif', category='error')
                return render_template(pages[iterator]['url'], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            if montant > players[session["ID"]]["flouze"]:
                flash('Le montant indiqué dépasse votre solde', category='error')
                return render_template(pages[iterator]['url'], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            players[session["ID"]]["flouze"] -= montant
            players[session["ID"]]["choix"] = montant
            players[session["ID"]]["done"] = True
            done += 1
            flash(Markup('Vous avez versé ' + str(montant) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin"> dans le pot commun'), category='success')
            if done == 5:
                pot_commun = 0
                for i in players:
                    pot_commun += i["choix"]
                prize = round(pot_commun * pages[iterator]["prize"] / 5)
                for i in players:
                    i["flouze"] += prize
                    i["message"] = Markup("Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin">')
            update_data()

        if pages[iterator]['url'] == "Jeu4-choix.html":
            if request.form['boutton'] == '0':
                players[session["ID"]]["choix"] = 0
            if request.form['boutton'] == '1':
                players[session["ID"]]["choix"] = 1
            if request.form['boutton'] == '2':
                players[session["ID"]]["choix"] = 2
            if request.form['boutton'] == '3':
                players[session["ID"]]["choix"] = 3
            if request.form['boutton'] == '4':
                players[session["ID"]]["choix"] = 4
            if request.form['boutton'] == "Jeu4-choix":
                if players[session["ID"]]["choix"] == None:
                    flash('Veuiller choisir un nombre', category='error')
                    return render_template(pages[iterator]['url'], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players, pages=pages)
                players[session["ID"]]["done"] = True
                done += 1
                if bonus_jeu4 == 0:
                    prize = pages[iterator]['prize'][i]
                elif bonus_jeu4 == 1:
                    prize = pages[iterator]['prizeBonus'][i]
                else:
                    prize = pages[iterator]['prizeDoubleBonus'][i]
                if prize[players[session["ID"]]["choix"]] == "star":
                    flash(Markup('Vous avez choisis le prix : <i class="fa fa-star"></i>'), category='success')
                else:
                    flash(Markup('Vous avez choisis le prix : ' + str(prize[players[session["ID"]]["choix"]]) + ' <img src="/static/images/coin.png" style="width:25px" alt="Coin">'), category='success')
                if done == 5:
                    iterator += 1
                    for i in players:
                        i["done"] = False
                    done = 0
                update_data()

        if request.form['boutton'] == "envoyer etoile":
            destinataire = request.form.get('destinataire')
            montant = request.form.get('quantité')
            if destinataire == None:
                flash('Veuiller choisir un destinataire', category='error')
                return render_template("don_etoiles.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            if montant == '':
                flash('Veuiller indiquer un montant', category='error')
                return render_template("don_etoiles.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            destinataire = int(destinataire)
            montant = int(montant)
            if montant < 1:
                flash('Le montant à envoyer ne peut pas être negatif ou nul', category='error')
                return render_template("don_etoiles.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            if montant > players[session["ID"]]["stars"]:
                flash("Vous n'avez pas assez d'étoiles", category='error')
                return render_template("don_etoiles.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
            players[session["ID"]]["stars"] -= montant
            players[otherPlayers[destinataire]["ID"]]["stars"] += montant
            flash(Markup('Vous avez envoyé ' + str(montant) + ' <i class="fa fa-star"></i> à ' + otherPlayers[destinataire]["name"]), category='success')
            update_data()
            return render_template("don_etoiles.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)

        if request.form['boutton'] == "léguer etoiles":
            return render_template("don_etoiles.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)

        if request.form['boutton'] == "terminer":
            players[session["ID"]]["done"] = True
            done += 1
            if done == 5:
                iterator += 1
                for i in players:
                    i["done"] = False
                done = 0

        if request.form['boutton'] == 'Jeu5-choix':
            for p in otherPlayers:
                p["message"] = ""
            destinataire = request.form.get('destinataire')



    if done == 5:
        return render_template("results.html", user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
    if players[session["ID"]]["done"]:
        return render_template("en_attente.html", done=done, user=players[session["ID"]] , otherPlayers=otherPlayers, players=players)
    return render_template(pages[iterator]['url'], user=players[session["ID"]] , otherPlayers=otherPlayers, players=players, pages=pages)
