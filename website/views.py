from flask import Blueprint, render_template, request, flash, session, redirect, url_for, Markup
from . import pages, gameState, players, socketio, log
import random
import pickle
import datetime
import numpy as np
from flask_socketio import send, emit

views = Blueprint('views', __name__)

def update_data():
    with open("data.pck", 'wb') as file:
        pickle.dump((gameState, players, log), file)
    socketio.emit('changed', None, broadcast=True)

def check_all_done():
    return all(p['done'] for p in players)
def end_waiting():
    gameState['iterator'] += 1
    for p in players:
        p["done"] = False
    gameState['done'] = 0

def check_action_allowed(gameNb):
    if players[session["ID"]]["done"]: return render_template("en_attente.html", done=gameState['done'], user=players[session["ID"]], players=players)
    if pages[gameState['iterator']]['round'][0] != gameNb: return render_template(pages[gameState['iterator']]['url'], user=players[session["ID"]], players=players, page=pages[gameState['iterator']], gameState=gameState)
    return None

def game1_logic():
    assert check_all_done()
    lottery = []
    for p in players:
        lottery += [p["ID"]] * p["choix"]
        p["message"] = Markup("Vous n'avez pas gagné la lotterie <i class='fa fa-frown-o'></i>")
    if len(lottery) > 0:
        lotteryWinnerID = random.choice(lottery)
        prize = pages[gameState['iterator']]["prize"] // len(lottery)
        players[lotteryWinnerID]["flouze"] += prize
        players[lotteryWinnerID]["message"] = Markup("Vous avez gagné la lotterie ! <br> Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" style="width:25px" alt="Coin">')
        log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Le gagnant de la lotterie est " + players[lotteryWinnerID]["name"] + " qui a reçu " + str(prize) + " Pièces")
    else:
        log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Il n'y a pas de gagnant à la lotterie car personne n'a participé")


def game2_logic():
    assert check_all_done()
    for i in range(1, 6):
        count = 0 #nombre  de fois que i a été choisis
        player = None
        for p in players:
            if p["choix"] == i:
                count += 1
                player = p #joueur gagnant
        if count == 1:
            prize = pages[gameState['iterator']]["prize"]*i
            player["flouze"] += prize
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a remporté " + str(prize) + "Pièces")
            for p in players:
                p["message"] = Markup(player["name"] + " a gagné et a remporté " + str(prize) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin">')
            break
    else:
        log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Personne n'a remporté de lot a cette manche")
        for p in players: # initialiser les messages
            p["message"] = "Personne n'a remporté de lot a cette manche"


def game3_init():
    for p in players:
        p["saved_flouze"] = max(0, p["flouze" ]- pages[gameState['iterator']]['initial_flouze'])
        p["flouze"] = pages[gameState['iterator']]['initial_flouze']
    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "L'argent des joueurs à été mis de coté. Ils leur restent tous " + str(pages[gameState['iterator']]['initial_flouze']) + " Pièces")

def game3_logic():
    assert check_all_done()
    pot_commun = 0
    pot_commun = sum(p["choix"] for p in players)
    prize = int(pot_commun * pages[gameState['iterator']]["gain"] // 5)
    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + str(prize*5) + " Pièces ont été redistribué équitablement à tous les joueurs ce qui fait " + str(prize) + " Pièces par joueur")
    for p in players:
        p["flouze"] += prize
        p["message"] = Markup("Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin">')

def game3_done():
    for p in players:
        p["flouze"] += p["saved_flouze"]
        p["saved_flouze"] = 0
    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "L'argent mis de coté à été remis en jeu")


def game4_logic():
    assert check_all_done()
    uniqueChoices = 0 # compte le nombre de choix uniques
    for p in players:
        p['message'] = "Vous n'avez pas remporté le prix"
    for i in range(5):
        count = 0 # nombre de fois que le prix i a été choisis
        player = None
        for p in players:
            if p["choix"] == i:
                count += 1
                player = p
        if count == 1:
            uniqueChoices += 1
            prize = pages[gameState['iterator']]['prize'][gameState["game4_bonus"]][i]
            if prize == "star":
                player["stars"] += 1
                player["message"] = Markup('Vous avez remporté le prix : <i class="fa fa-star"></i>')
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a gagné une étoile")
            else:
                player["flouze"] += prize
                player["message"] = Markup("Vous avez remporté le prix : " + str(prize) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin">')
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a remporté " + str(prize) + "Pièces")
    if uniqueChoices == 5:
        if pages[gameState['iterator']]['round'][1] == 3:
            gameState["masterPrizeBonus"] = True
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Tous les joueurs ont choisis un prix différent donc le gros lot passe de 25000 à 30000 Pièces")
        else:
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Tous les joueurs ont choisis un prix différent donc un bonus s'applique pour la manche suivante")
            gameState["game4_bonus"] += 1


def game5_logic():
    assert check_all_done()
    pass



@views.route('/', methods=['GET', 'POST'])
def home():
    global gameState

    if "ID" not in session :
        return redirect(url_for('auth.login'))

    if session["ID"] == "admin":
        if request.method == 'POST':
            assert request.form['boutton'] in ['page suivante', "page précedente"]
            if request.form['boutton'] == 'page suivante' and gameState['iterator'] < len(pages)-1:
                if pages[gameState['iterator']]['url'] == "results.html":
                    for p in players: #reinitialiser le statut et les choix des joueurs
                        p["choix"] = None
                gameState['iterator'] += 1
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Passage à la page suivante : " + pages[gameState['iterator']]['url'] + " (jeu " + str(pages[gameState['iterator']]['round'][0]) + ", manche " + str(pages[gameState['iterator']]['round'][1]) + ")")

                if pages[gameState['iterator']]['url'] == "Jeu3-title.html": #mettre de coté le Flouze
                    game3_init()

                if pages[gameState['iterator']]['url'] == "Jeu4-title.html": #rassembler le Flouze
                    game3_done()

                update_data()

            if request.form['boutton'] == 'page précedente' and gameState['iterator'] > 0:
                for p in players:
                    p["choix"] = False
                    p["done"] = False
                gameState['done'] = 0
                gameState['iterator'] -= 1
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Revenir à la page précedente : " + pages[gameState['iterator']]['url'] + " (jeu " + str(pages[gameState['iterator']]['round'][0]) + ", manche " + str(pages[gameState['iterator']]['round'][1]) + ")")
                update_data()

        return render_template("monitoring.html" , players=players, pages=pages, iterator=gameState['iterator'], log=log, imax=min(len(log),10))

    #otherPlayers = players.copy()
    #if pages[gameState['iterator']]['url'] == "Jeu 5":
    #    otherPlayers.pop(winner['ID'])
    #else:
    #    otherPlayers.pop(session["ID"])

    if request.method == 'POST':

        if request.form['boutton'] == 'don':
            return render_template("faire_un_don.html", user=players[session["ID"]], players=players)

        if request.form['boutton'] == "envoyer don":
            destinataire_level = request.form.get('destinataire')
            montant = request.form.get('montant')
            if destinataire_level == None:
                flash('Veuiller choisir un destinataire', category='error')
                return render_template("faire_un_don.html", user=players[session["ID"]], players=players)
            if montant == '':
                flash('Veuiller indiquer un montant', category='error')
                return render_template("faire_un_don.html", user=players[session["ID"]], players=players)
            destinataire_level = int(destinataire_level)
            montant = int(montant)
            if montant < 1:
                flash('Le montant à envoyer ne peut pas être negatif ou nul', category='error')
                return render_template("faire_un_don.html", user=players[session["ID"]], players=players)
            if montant > players[session["ID"]]["flouze"]:
                flash('Le montant indiqué dépasse votre solde', category='error')
                return render_template("faire_un_don.html", user=players[session["ID"]], players=players)
            players[session["ID"]]["flouze"] -= montant
            otherPlayers = players[session["ID"]]['otherPlayers']
            destinataireID = otherPlayers[destinataire_level]
            players[destinataireID]["flouze"] += montant
            flash(Markup('Vous avez envoyé ' + str(montant) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin"> à ' + players[destinataireID]["name"]), category='success')
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[session["ID"]]["name"] + " a fait un don de " + str(montant) + " Pièces à " + players[destinataireID]["name"])
            update_data()
            return render_template(pages[gameState['iterator']]['url'], user=players[session["ID"]], players=players, page=pages[gameState['iterator']], gameState=gameState)

        if request.form['boutton'] == "jeu1-choix":
            action = check_action_allowed(1)
            if action: return action
            tickets = request.form.get('tickets')
            if tickets == None:
                flash('Veuiller faire un choix', category='error')
                return render_template(pages[gameState['iterator']]['url'], user=players[session["ID"]], players=players)
            players[session["ID"]]["choix"] = int(tickets)
            players[session["ID"]]["done"] = True
            gameState['done'] += 1
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[session["ID"]]["name"] + " a choisis " + tickets + " tickets")
            flash('Vous avez choisis ' + tickets + ' tickets', category='success')
            if gameState['done'] == 5:
                game1_logic()
                end_waiting()
            update_data()

        if pages[gameState['iterator']]['url'] == "Jeu2-choix.html":
            action = check_action_allowed(2)
            if action: return action
            if request.form['boutton'] == "validate num":
                if players[session["ID"]]["choix"] == None:
                    flash('Veuiller choisir un nombre', category='error')
                    return render_template(pages[gameState['iterator']]['url'], user=players[session["ID"]], players=players)
                players[session["ID"]]["done"] = True
                gameState['done'] += 1
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[session["ID"]]["name"] + " a choisis le nombre " + str(players[session["ID"]]["choix"]))
                flash('Vous avez choisis le nombre ' + str(players[session["ID"]]["choix"]), category='success')
                if gameState['done'] == 5:
                    game2_logic()
                    end_waiting()
                update_data()
            else:
                players[session["ID"]]["choix"] = int(request.form['boutton'])

        if request.form['boutton'] == "Jeu3-choix":
            action = check_action_allowed(3)
            if action: return action
            montant = request.form.get('montant')
            if montant == '':
                flash(Markup('Veuiller indiquer un montant<br>(0 si vous ne voulez rien investir)'), category='error')
                return render_template(pages[gameState['iterator']]['url'], user=players[session["ID"]], players=players)
            montant = int(montant)
            if montant < 0:
                flash('Le montant à investir ne peut pas être negatif', category='error')
                return render_template(pages[gameState['iterator']]['url'], user=players[session["ID"]], players=players)
            if montant > players[session["ID"]]["flouze"]:
                flash('Le montant indiqué dépasse votre solde', category='error')
                return render_template(pages[gameState['iterator']]['url'], user=players[session["ID"]], players=players)
            players[session["ID"]]["flouze"] -= montant
            players[session["ID"]]["choix"] = montant
            players[session["ID"]]["done"] = True
            gameState['done'] += 1
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[session["ID"]]["name"] + " a versé " + str(montant) + " Pièces dans le pot commun")
            flash(Markup('Vous avez versé ' + str(montant) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin"> dans le pot commun'), category='success')
            if gameState['done'] == 5:
                game3_logic()
                end_waiting()
            update_data()

        if pages[gameState['iterator']]['url'] == "Jeu4-choix.html":
            action = check_action_allowed(4)
            if action: return action
            if request.form['boutton'] == "Jeu4-choix":
                if players[session["ID"]]["choix"] == None:
                    flash('Veuiller choisir un nombre', category='error')
                    return render_template(pages[gameState['iterator']]['url'], user=players[session["ID"]], players=players, page=pages[gameState['iterator']], gameState=gameState)
                players[session["ID"]]["done"] = True
                gameState['done'] += 1
                prize = pages[gameState['iterator']]['prize'][gameState["game4_bonus"]]
                if prize[players[session["ID"]]["choix"]] == "star":
                    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[session["ID"]]["name"] + " a choisis l'etoile")
                    flash(Markup('Vous avez choisis le prix : <i class="fa fa-star"></i>'), category='success')
                else:
                    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[session["ID"]]["name"] + " a choisis le prix : " + str(prize[players[session["ID"]]["choix"]]) + " Pièces")
                    flash(Markup('Vous avez choisis le prix : ' + str(prize[players[session["ID"]]["choix"]]) + ' <img src="/static/images/coin.png" style="width:25px" alt="Coin">'), category='success')
                if gameState['done'] == 5:
                    game4_logic()
                    end_waiting()
                update_data()
            else:
                players[session["ID"]]["choix"] = int(request.form['boutton'])

        if request.form['boutton'] == "envoyer etoile":
            destinataire_level = request.form.get('destinataire')
            montant = request.form.get('quantité')
            if destinataire_level == None:
                flash('Veuiller choisir un destinataire', category='error')
                return render_template("don_etoiles.html", user=players[session["ID"]], players=players)
            if montant == '':
                flash('Veuiller indiquer un montant', category='error')
                return render_template("don_etoiles.html", user=players[session["ID"]], players=players)
            destinataire_level = int(destinataire_level)
            montant = int(montant)
            if montant < 1:
                flash('Le montant à envoyer ne peut pas être negatif ou nul', category='error')
                return render_template("don_etoiles.html", user=players[session["ID"]], players=players)
            if montant > players[session["ID"]]["stars"]:
                flash("Vous n'avez pas assez d'étoiles", category='error')
                return render_template("don_etoiles.html", user=players[session["ID"]], players=players)
            players[session["ID"]]["stars"] -= montant
            otherPlayers = players[session["ID"]]['otherPlayers']
            destinataireID = otherPlayers[destinataire_level]
            players[destinataireID]["stars"] += montant
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[session["ID"]]["name"] + " a légué une étoile à " + players[otherPlayers[destinataire]["ID"]]["name"])
            flash(Markup('Vous avez envoyé ' + str(montant) + ' <i class="fa fa-star"></i> à ' + otherPlayers[destinataire]["name"]), category='success')
            update_data()
            return render_template("don_etoiles.html", user=players[session["ID"]], players=players)

        if request.form['boutton'] == "léguer etoiles":
            return render_template("don_etoiles.html", user=players[session["ID"]], players=players)

        if request.form['boutton'] == "terminer":
            players[session["ID"]]["done"] = True
            gameState['done'] += 1
            if gameState['done'] == 5:
                stars = []
                for p in players:
                    stars.append(p['stars'])
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + str(stars))
                winnerID = np.argmax(stars)
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + 'Le gaganant est : ' + str(winnerID) + players[winnerID]['name'] + str(max(stars)))
                if stars.count(max(stars)) == 1:
                    winner = players[winnerID]
                    for p in players:
                        if p == winner:
                            p['message'] = Markup("Vous avez le plus d'étoiles et êtes ainsi en possesionde la somme de " + str(pages[gameState['iterator']+1]['prize']) + ' <img src="/static/images/coin.png" style="width:25px" alt="Coin"> pour le 5ème jeu')
                        else:
                            p['message'] = Markup(winner['name'] + " a le plus d'étoiles et est ainsi en possesionde la somme de " + str(pages[gameState['iterator']+1]['prize']) + ' <img src="/static/images/coin.png" style="width:25px" alt="Coin"> pour le 5ème jeu')
                else:
                    for p in players:
                        p['message'] = "Dû à une égalité en terme d'étoiles, personne ne remporte le gros lot et le cinquième jeu est annulé"
                update_data()

        if pages[gameState['iterator']]['url'] == "Jeu 5":

            if request.form['boutton'] == 'Jeu5-choix':
                for p in otherPlayers:
                    montant = request.form.get(p['name'])
                    pages[gameState['iterator']]['propositions'].append(montant)
                    p["message"] = Markup(players[session["ID"]]['name'] + 'vous fait une proposition de ' + str(montant) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin">')
                pages[gameState['iterator']]['validation'] = True
                update_data()

            elif request.form['boutton'] == 'nouvelle proposition':
                return render_template("Jeu5-choix.html", user=players[session["ID"]], otherPlayers=otherPlayers)

            else:
                players[session['ID']]['choix'] = int(request.form['boutton'])
                gameState['done'] += 1
                if gameState['done'] == 4:
                    pages[gameState['iterator']]['essais'] -= 1
                    v = 0
                    for p in otherPlayers:
                        v += p['choix']
                    if v == 4:
                        winner['message'] = "votre proposition a été acceptée"
                        for i in range(4):
                            otherPlayers[i]['message'] = Markup("La proposition à été acceptée par tous les joueurs.\n Vous avez recu " + pages[gameState['iterator']]['propositions'][i] + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin">')
                        gameState['done'] = 5
                    else:
                        if pages[gameState['iterator']]['essais'] == 0:
                            for p in players:
                                p['message'] = "Auccun accord à été trouvé apprès ces 3 essais donc personne n'a remporté quoi que ce soit"
                            gameState['done'] = 5
                        else:
                            gameState['done'] = 0
                            pages[gameState['iterator']]['validation'] = False
                    update_data()

    if request.method == 'GET':
        if players[session["ID"]]["done"]:
            return render_template("en_attente.html", done=gameState['done'], user=players[session["ID"]], players=players)

        if pages[gameState['iterator']]['url'] == 'Jeu 5':
            if pages[gameState['iterator']]['validation']:
                if playeers[session['ID']] == winner:
                    return render_template("en_attente_jeu5.html", user=players[session["ID"]], players=players, done=gameState['done'], sur4=True)
                else:
                    return render_template("Jeu5-Valider.html", user=players[session["ID"]], players=players)

            else:
                if players[session['ID']] == winner:
                    return render_template("Jeu-reveal.html", user=players[session["ID"]], players=otherPlayers, propositions=propositions)
                else:
                    return render_template("en_attente_jeu5.html", user=players[session["ID"]], players=players, done=gameState['done'], sur4=False)
    if players[session["ID"]]["done"]:
        return render_template("en_attente.html", done=gameState['done'], user=players[session["ID"]], players=players)
    return render_template(pages[gameState['iterator']]['url'], user=players[session["ID"]], players=players, page=pages[gameState['iterator']], gameState=gameState)
