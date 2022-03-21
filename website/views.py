from flask import Blueprint, render_template, request, flash, session, redirect, url_for, Markup
from . import pages, pages_by_round, gameState, players, socketio, log, theme_colors, quiz

from flask_socketio import send, emit

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    global gameState

    if "ID" not in session :
        return redirect(url_for('auth.login'))

    if session["ID"] == "admin":
        if request.method == 'POST':
            assert 'boutton' in request.form and request.form['boutton'] in ['page suivante', 'page précedente'] or\
                   'reveal' in request.form and request.form['reveal'] in map(str, range(5)) or\
                   'diapo' in request.form and request.form['diapo'] in ['suivant', 'précedent']
            if 'reveal' in request.form:
                reveal_card(int(request.form['reveal']))
            elif 'diapo' in request.form:
                if request.form['diapo'] == 'suivant':
                    next_frame()
                if request.form['diapo'] == 'précedent':
                    previous_frame()
            elif request.form['boutton'] == 'page suivante' and gameState['iterator'] < len(pages)-1:
                if pages[gameState['iterator']]['url'] == "results.html":
                    for p in players: # reinitialiser le statut et les choix des joueurs
                        p["choix"] = None
                        p["gain_a_partager"] = 0
                        p["reveal"] = False
                if pages[gameState['iterator']]['url'] == "title.html":
                    gameState["frameId"] = 0
                gameState['iterator'] += 1
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Passage à la page suivante : " + pages[gameState['iterator']]['url'] + " (jeu " + str(pages[gameState['iterator']]['round'][0]) + ", manche " + str(pages[gameState['iterator']]['round'][1]) + ")")

                if pages[gameState['iterator']]['round'] == [3, 0]: # mettre de coté le Flouze
                    game3_init()
                if pages[gameState['iterator']]['round'] == [4, 0]: # rassembler le Flouze
                    game3_done()
                if pages[gameState['iterator']]['round'] == [5, 0]:
                    game5_init()
                save_data()
                refresh_all_pages()

            elif request.form['boutton'] == 'page précedente' and gameState['iterator'] > 0:
                next_frame()
                return render_template("monitoring.html" , players=players, pages=pages, gameState=gameState, log=log, imax=min(len(log),20))

                for p in players:
                    p["choix"] = False
                    p["done"] = False
                gameState['done'] = 0
                gameState['iterator'] -= 1
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Revenir à la page précedente : " + pages[gameState['iterator']]['url'] + " (jeu " + str(pages[gameState['iterator']]['round'][0]) + ", manche " + str(pages[gameState['iterator']]['round'][1]) + ")")
                save_data()
                refresh_all_pages()


        return render_template("monitoring.html" , players=players, pages=pages, gameState=gameState, log=log, imax=min(len(log),20))

    player = players[session['ID']]
    if request.method == 'POST':

        if request.form['boutton'] == 'partager':
            return render_template("partager.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])

        if request.form['boutton'] == 'don':
            return render_template("faire_un_don.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])

        if request.form['boutton'] == 'en fait non':
            return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], secondary_theme_color=theme_colors[pages[gameState['iterator']]['background']][1], user=player, players=players, page=pages[gameState['iterator']], gameState=gameState, background=pages[gameState['iterator']]['background'])

        if request.form['boutton'] == "envoyer don":
            receiver_level = request.form.get('destinataire')
            montant = request.form.get('montant')
            if receiver_level == None:
                flash('Veuillez choisir un destinataire!', category='error')
                return render_template("faire_un_don.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            if montant == '':
                flash('Veuiller indiquer un montant', category='error')
                return render_template("faire_un_don.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            receiver_level = int(receiver_level)
            montant = int(montant)
            if montant < 1:
                flash('Le montant à envoyer ne peut pas être negatif ou nul', category='error')
                return render_template("faire_un_don.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            if montant > player["flouze"]:
                flash('Le montant indiqué dépasse votre solde', category='error')
                return render_template("faire_un_don.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            
            TODO

            save_data()
            return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, page=pages[gameState['iterator']], gameState=gameState, background=pages[gameState['iterator']]['background'])

        if request.form['boutton'] == "envoi partager":
            montants = []
            for receiver in player['otherPlayers']:
                montant = request.form.get(receiver['name'])
                montant = 0 if montant == '' else int(montant)
                if montant < 0:
                    flash('Vous ne pouvez pas envoiyer des montants négatifs !', category='error')
                    return render_template("partager.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
                montants.append(montant)
            if sum(montants) > player["gain_a_partager"]:
                flash('Vous ne pouvez pas donner plus que ce que vous avez reçu !', category='error')
                return render_template("partager.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            player["gain_a_partager"] = 0
            
            TODO

            save_data()
            return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, page=pages[gameState['iterator']], gameState=gameState, background=pages[gameState['iterator']]['background'])

        if request.form['boutton'] == "jeu1-choix":
            action = check_action_allowed(player, 1)
            if action: return action
            tickets = request.form.get('tickets')
            if tickets == None:
                flash('Veuiller faire un choix', category='error')
                return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            player["choix"] = int(tickets)
            player["done"] = True
            gameState['done'] += 1
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a choisis " + tickets + " tickets")
            flash('Vous avez choisis ' + tickets + ' tickets', category='success')
            if gameState['done'] < 5:
                update_waiting_count(gameState["done"], 5)
            else:
                game1_logic()
                end_waiting()
            save_data()

        if pages[gameState['iterator']]['url'] == "Jeu2-choix.html":
            action = check_action_allowed(player, 2)
            if action: return action
            if request.form['boutton'] == "validate num":
                if player["choix"] == None:
                    flash('Veuiller choisir un nombre', category='error')
                    return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
                player["done"] = True
                gameState['done'] += 1
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a choisis le nombre " + str(player["choix"]))
                flash('Vous avez choisis le nombre ' + str(player["choix"]), category='success')
                if gameState['done'] < 5:
                    update_waiting_count(gameState["done"], 5)
                else:
                    game2_logic()
                    end_waiting()
                save_data()
            else:
                player["choix"] = int(request.form['boutton'])

        if request.form['boutton'] == "Jeu3-choix":
            action = check_action_allowed(player, 3)
            if action: return action
            montant = request.form.get('montant')
            if montant == '':
                flash(Markup('Veuiller indiquer un montant<br>(0 si vous ne voulez rien investir)'), category='error')
                return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            montant = int(montant)
            if montant < 0:
                flash('Le montant à investir ne peut pas être negatif', category='error')
                return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            if montant > player["flouze"]:
                flash('Le montant indiqué dépasse votre solde', category='error')
                return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            player["flouze"] -= montant
            player["choix"] = montant
            player["done"] = True
            gameState['done'] += 1
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a versé " + str(montant) + " Pièces dans le pot commun")
            flash(Markup('Vous avez versé ' + str(montant) + ' <img src="/static/images/coin.png" style="width:22px" alt="Coin"> dans le pot commun'), category='success')
            if gameState['done'] < 5:
                update_waiting_count(gameState["done"], 5)
            else:
                game3_logic()
                end_waiting()
            save_data()

        if pages[gameState['iterator']]['url'] == "Jeu4-choix.html":
            action = check_action_allowed(player, 4)
            if action: return action
            if request.form['boutton'] == "Jeu4-choix":
                if player["choix"] == None:
                    flash('Veuiller choisir un nombre', category='error')
                    return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, page=pages[gameState['iterator']], gameState=gameState, background=pages[gameState['iterator']]['background'])
                player["done"] = True
                gameState['done'] += 1
                prize = pages[gameState['iterator']]['prize'][gameState["game4_bonus"]]
                if prize[player["choix"]] == "star":
                    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a choisis l'etoile")
                    flash(Markup('Vous avez choisis le prix : <i class="fa fa-star"></i>'), category='success')
                else:
                    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a choisis le prix : " + str(prize[player["choix"]]) + " Pièces")
                    flash(Markup('Vous avez choisis le prix : ' + str(prize[player["choix"]]) + ' <img src="/static/images/coin.png" style="width:25px" alt="Coin">'), category='success')
                if gameState['done'] < 5:
                    update_waiting_count(gameState["done"], 5)
                else:
                    game4_logic()
                    end_waiting()
                save_data()
            else:
                player["choix"] = int(request.form['boutton'])

        if request.form['boutton'] == "envoyer etoile":
            receiver_level = request.form.get('destinataire')
            montant = request.form.get('quantité')
            if receiver_level == None:
                flash('Veuiller choisir un destinataire!', category='error')
                return render_template("don_etoiles.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            if montant == '':
                flash('Veuiller indiquer un montant', category='error')
                return render_template("don_etoiles.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            receiver_level = int(receiver_level)
            montant = int(montant)
            if montant < 1:
                flash('Le montant à envoyer ne peut pas être negatif ou nul', category='error')
                return render_template("don_etoiles.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            if montant > player["stars"]:
                flash("Vous n'avez pas assez d'étoiles", category='error')
                return render_template("don_etoiles.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            
            
            
            
            otherPlayers = player['otherPlayers']
            receiver = otherPlayers[receiver_level]
            
            TODO


            save_data()
            return render_template("don_etoiles.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])

        if request.form['boutton'] == "léguer etoiles":
            return render_template("don_etoiles.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])

        if request.form['boutton'] == "terminer":
            player["done"] = True
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
            save_data()

        if pages[gameState['iterator']]['url'] == "Jeu 5":
            if request.form['boutton'] == 'quiz':
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + f'{player["name"]} a donner la réponse "{request.form.get("réponse")}" au quiz')
                gameState['questions'] += 1
                op = gameState['otherPlayers'].copy()
                op.remove(gameState['otherPlayers'][gameState['questions']])
                for i in range(3):
                    op[i]['question'] = quiz[gameState['questions']][i]

            if request.form['boutton'] == 'proposition':
                total = 0
                for p in gameState['otherPlayers']:
                    montant = request.form.get(p['name'])
                    if montant == '':
                        flash('Veuiller indiquer un montant pour tous les joueurs', category='error')
                        return render_template("Jeu5-proposition.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, otherPlayers=gameState['otherPlayers'], background=pages[gameState['iterator']]['background'])
                    montant = int(montant)
                    total += montant
                if total > gameState['starMaster']['flouze']:
                    flash('Les propositions que vous avez faites dépasse vos moyens', category='error')
                    return render_template("Jeu5-proposition.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, otherPlayers=gameState['otherPlayers'], background=pages[gameState['iterator']]['background'])
                for p in gameState['otherPlayers']:
                    montant = int(request.form.get(p['name']))
                    p["proposition"] = montant
                    p["message"] = Markup(player['name'] + ' vous fait une proposition de ' + str(montant) + ' <img src="/static/images/coin.png" style="width:22px" alt="Coin">')
                gameState['iterator'] += 1
                refresh_all_pages()


            elif request.form['boutton'] in ["0", "1"]:
                if player["done"]: pass
                players[session['ID']]['choix'] = int(request.form['boutton'])
                player["done"] = True
                gameState['done'] += 1

                if gameState['done'] < 4:
                    update_waiting_count(gameState["done"], 4)
                else:
                    if sum(p['choix'] for p in gameState['otherPlayers']) >= 3:
                        gameState['starMaster']['message'] = "Votre proposition a été acceptée par la majorité"
                        for p in gameState['otherPlayers']:
                            gameState['starMaster']['flouze'] -= p['proposition']
                            p['flouze'] += p['proposition']
                            p['message'] = Markup(f'La proposition à été acceptée par la majorité des joueurs.\n Vous avez recu {p["proposition"]} <img src="/static/images/coin.png" style="width:22px" alt="Coin">')
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
                refresh_all_pages()
            save_data()

    if pages[gameState['iterator']]['url'] == "Jeu 5":
        if player["done"]:
            return render_template("en_attente_jeu5.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], done=gameState['done'], user=player, players=players, background=pages[gameState['iterator']]['background'])

        if pages[gameState['iterator']]["phase"] == "proposition":
            if players[session['ID']] == gameState['starMaster']:
                return render_template("Jeu5-proposition.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, otherPlayers=gameState['otherPlayers'], background=pages[gameState['iterator']]['background'])
            elif gameState['remaining_trials'] == 3 and gameState['questions'] < 4:
                if player['name'] == gameState['otherPlayers'][gameState['questions']]['name']:
                    return render_template("quiz.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], secondary_theme_color=theme_colors[pages[gameState['iterator']]['background']][1], user=player, background=pages[gameState['iterator']]['background'], input=True)
                else:
                    return render_template("quiz.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], secondary_theme_color=theme_colors[pages[gameState['iterator']]['background']][1], user=player, background=pages[gameState['iterator']]['background'], input=False)
            else:
                return render_template("results.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
        elif pages[gameState['iterator']]["phase"] == "validation":
            if players[session['ID']] == gameState['starMaster']:
                return render_template("en_attente_jeu5.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, done=gameState['done'], background=pages[gameState['iterator']]['background'])
            else:
                return render_template("Jeu5-Valider.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, background=pages[gameState['iterator']]['background'])
        elif pages[gameState['iterator']]["phase"] == "reveal":
            if players[session['ID']] == gameState['starMaster']:
                return render_template("Jeu5-reveal.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, otherPlayers=gameState['otherPlayers'], background=pages[gameState['iterator']]['background'])
            else:
                return render_template("results.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])

    if player["done"]:
        return render_template("en_attente.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], done=gameState['done'], user=player, players=players, background=pages[gameState['iterator']]['background'])

    return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], secondary_theme_color=theme_colors[pages[gameState['iterator']]['background']][1], user=player, players=players, page=pages[gameState['iterator']], gameState=gameState, background=pages[gameState['iterator']]['background'])
