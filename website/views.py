from flask import Blueprint, render_template, request, flash, session, redirect, url_for, Markup
from . import pages, pages_by_round, gameState, players, socketio, log
import random
import pickle
import datetime
import numpy as np
from flask_socketio import send, emit

views = Blueprint('views', __name__)

def send_message(player, msg):
    socketio.emit('message', msg, room=player['sid'])

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
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + f"Tous les joueurs ont choisis un prix différent donc le gros lot passe de {pages_by_round[(5, 0)]['prize']} à {pages_by_round[(5, 0)]['prize'] + pages_by_round[(5, 0)]['bonus']} Pièces")
        else:
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Tous les joueurs ont choisis un prix différent donc un bonus s'applique pour la manche suivante")
            gameState["game4_bonus"] += 1


def game5_init():
    for p in gameState['otherPlayers']:
        p['message'] = f"Veuillez attendre la proposition de {gameState['starMaster']['name']} ..."

def game5_done():
    gameState['iterator'] = len(pages) - 1
    for p in players:
        p["done"] = False
    gameState['done'] = 0

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

                if pages[gameState['iterator']]['url'] == "Jeu5-title.html":
                    game5_init()

                update_data()

            if request.form['boutton'] == 'page précedente' and gameState['iterator'] > 0:
                send_message(players[0], "kikou")
                return render_template("monitoring.html" , players=players, pages=pages, iterator=gameState['iterator'], log=log, imax=min(len(log),10))

                for p in players:
                    p["choix"] = False
                    p["done"] = False
                gameState['done'] = 0
                gameState['iterator'] -= 1
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Revenir à la page précedente : " + pages[gameState['iterator']]['url'] + " (jeu " + str(pages[gameState['iterator']]['round'][0]) + ", manche " + str(pages[gameState['iterator']]['round'][1]) + ")")
                update_data()

        return render_template("monitoring.html" , players=players, pages=pages, iterator=gameState['iterator'], log=log, imax=min(len(log),10))

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
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[session["ID"]]["name"] + " a légué une étoile à " + players[destinataireID]["name"])
            flash(Markup('Vous avez envoyé ' + str(montant) + ' <i class="fa fa-star"></i> à ' + players[destinataireID]["name"]), category='success')
            update_data()
            return render_template("don_etoiles.html", user=players[session["ID"]], players=players)

        if request.form['boutton'] == "léguer etoiles":
            return render_template("don_etoiles.html", user=players[session["ID"]], players=players)

        if request.form['boutton'] == "terminer":
            players[session["ID"]]["done"] = True
            gameState['done'] += 1
            if gameState['done'] == 5:
                stars = [p['stars'] for p in players]
                winnerID = np.argmax(stars)
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + f"Le nombre d'etoiles pour chaque joueur est respectivement : {stars}")
                if stars.count(max(stars)) == 1:
                    gameState['starMaster'] = players[winnerID]
                    gameState['starMaster']['flouze'] += pages_by_round[(5, 0)]['prize'] + pages_by_round[(5, 0)]['bonus'] * gameState['masterPrizeBonus']
                    gameState['otherPlayers'].remove(players[winnerID])
                    for p in players:
                        p['message'] = Markup(f"{gameState['starMaster']['name']} a le plus d'étoiles et est ainsi en possesion de la somme de {pages_by_round[(5, 0)]['prize'] + pages_by_round[(5, 0)]['bonus'] * gameState['masterPrizeBonus']} <img src='/static/images/coin.png' style='width:25px' alt='Coin'> pour le 5ème jeu")
                    gameState['starMaster']['message'] = Markup(f"Vous avez le plus d'étoiles et êtes ainsi en possesion de la somme de {pages_by_round[(5, 0)]['prize'] + pages_by_round[(5, 0)]['bonus'] * gameState['masterPrizeBonus']} <img src='/static/images/coin.png' style='width:25px' alt='Coin'> pour le 5ème jeu")
                    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + f"{gameState['starMaster']['name']} a le plus d'étoileset remporte ainsi la somme de {pages_by_round[(5, 0)]['prize']} pièces pour le cinquième jeu.")
                else:
                    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Dû à une égalité en terme d'étoiles, personne ne remporte le gros lot et le cinquième jeu est annulé")
                    for p in players:
                        p['message'] = "Dû à une égalité en terme d'étoiles, personne ne remporte le gros lot et le cinquième jeu est annulé"
                end_waiting()
            update_data()

        if pages[gameState['iterator']]['url'] == "Jeu 5":
            if request.form['boutton'] == 'proposition':
                total = 0
                for p in gameState['otherPlayers']:
                    montant = request.form.get(p['name'])
                    if montant == '':
                        flash('Veuiller indiquer un montant pour tous les joueurs', category='error')
                        return render_template("Jeu5-proposition.html", user=players[session["ID"]], otherPlayers=gameState['otherPlayers'])
                    montant = int(montant)
                    total += montant
                if total > gameState['starMaster']['flouze']:
                    flash('Les propositions que vous avez faites dépasse vos moyens', category='error')
                    return render_template("Jeu5-proposition.html", user=players[session["ID"]], otherPlayers=gameState['otherPlayers'])
                for p in gameState['otherPlayers']:
                    montant = int(request.form.get(p['name']))
                    p["proposition"] = montant
                    p["message"] = Markup(players[session["ID"]]['name'] + ' vous fait une proposition de ' + str(montant) + ' <img src="/static/images/coin.png" style="width:30px" alt="Coin">')
                gameState['iterator'] += 1


            elif request.form['boutton'] in ["0", "1"]:
                if players[session["ID"]]["done"]: pass
                players[session['ID']]['choix'] = int(request.form['boutton'])
                players[session["ID"]]["done"] = True
                gameState['done'] += 1

                if gameState['done'] == 4:
                    if sum(p['choix'] for p in gameState['otherPlayers']) >= 3:
                        gameState['starMaster']['message'] = "Votre proposition a été acceptée par la majorité"
                        for p in gameState['otherPlayers']:
                            gameState['starMaster']['flouze'] -= p['proposition']
                            p['flouze'] += p['proposition']
                            p['message'] = Markup(f'La proposition à été acceptée par la majorité des joueurs.\n Vous avez recu {p["proposition"]} <img src="/static/images/coin.png" style="width:30px" alt="Coin">')
                        game5_done()
                    else:
                        gameState['remaining_trials'] -= 1
                        if gameState['remaining_trials'] == 0:
                            gameState['starMaster']['flouze'] -= pages_by_round[(5, 0)]['prize'] + pages_by_round[(5, 0)]['bonus'] * gameState['masterPrizeBonus']
                            gameState['starMaster']['message'] = Markup(f"Votre dernière proposition a été refusée par la majorité. Les {pages_by_round[(5, 0)]['prize'] + pages_by_round[(5, 0)]['bonus'] * gameState['masterPrizeBonus']} <img src='/static/images/coin.png' style='width:25px' alt='Coin'> vous sont donc retirés")
                            for p in gameState['otherPlayers']:
                                p['message'] = Markup(f"Auccun accord à été trouvé apprès ces 3 essais donc {gameState['starMaster']['name']} ne remporte pas les {pages_by_round[(5, 0)]['prize'] + pages_by_round[(5, 0)]['bonus'] * gameState['masterPrizeBonus']} <img src='/static/images/coin.png' style='width:25px' alt='Coin'>")
                            game5_done()
                        else:
                            gameState['starMaster']['message'] = "Votre proposition a été refusée par la majorité"
                            for p in gameState['otherPlayers']:
                                p['message'] = Markup(f"La proposition à été refusée par au moins 2 joueurs.\nEn attente d'une nouvelle proposition.")
                            end_waiting()
            elif request.form['boutton'] == 'nouvelle proposition':
                gameState['iterator'] -= 2

            update_data()

    if pages[gameState['iterator']]['url'] == "Jeu 5":
        if players[session["ID"]]["done"]:
            return render_template("en_attente_jeu5.html", done=gameState['done'], user=players[session["ID"]], players=players)

        if pages[gameState['iterator']]["phase"] == "proposition":
            if players[session['ID']] == gameState['starMaster']:
                return render_template("Jeu5-proposition.html", user=players[session["ID"]], otherPlayers=gameState['otherPlayers'])
            else:
                return render_template("results.html", user=players[session["ID"]], players=players)
        elif pages[gameState['iterator']]["phase"] == "validation":
            if players[session['ID']] == gameState['starMaster']:
                return render_template("en_attente_jeu5.html", user=players[session["ID"]], done=gameState['done'])
            else:
                return render_template("Jeu5-Valider.html", user=players[session["ID"]])
        elif pages[gameState['iterator']]["phase"] == "reveal":
            if players[session['ID']] == gameState['starMaster']:
                return render_template("Jeu5-reveal.html", user=players[session["ID"]], otherPlayers=gameState['otherPlayers'])
            else:
                return render_template("results.html", user=players[session["ID"]], players=players)

    if players[session["ID"]]["done"]:
        return render_template("en_attente.html", done=gameState['done'], user=players[session["ID"]], players=players)

    return render_template(pages[gameState['iterator']]['url'], user=players[session["ID"]], players=players, page=pages[gameState['iterator']], gameState=gameState)
