from flask import Blueprint, render_template, request, flash, session, redirect, url_for, Markup
<<<<<<< HEAD
=======
import config
from . import pages, pages_by_round, gameState, players, socketio, log, theme_colors, quiz
import random
import pickle
import datetime
import numpy as np
from flask_socketio import send, emit

views = Blueprint('views', __name__)

def refresh_all_pages():
    socketio.emit('refresh', None, broadcast=True)

def send_message(msg, player):
    socketio.emit('message', msg, room=player['sid'])

def save_data():
    global admin_sid
    with open("data.pck", 'wb') as file:
        pickle.dump((gameState, players, log), file)
    if config.admin_sid:
        socketio.emit('refresh', None, room=config.admin_sid)

def update_data(changes, players=None):
    if players:
        for player in players:
            if "sid" in player:
                socketio.emit('update_data', changes, room=player['sid'])
    else:
        socketio.emit('update_data', changes, broadcast=True)

def reveal_card(card_id):
    if gameState['reveal'][card_id]: return
    gameState['reveal'][card_id] = True
    socketio.emit('reveal_card', card_id, broadcast=True)
    save_data()

def next_frame():
    gameState['frameId'] += 1
    socketio.emit('move_to_frame', gameState['frameId'], broadcast=True)
    save_data()

def previous_frame():
    gameState['frameId'] -= 1
    socketio.emit('move_to_frame', gameState['frameId'], broadcast=True)
    save_data()

def update_waiting_count(count, total):
    update_data([("count", f"{count} / {total}")], players=(p  for p in players if p["done"]))


def check_all_done():
    return all(p['done'] for p in players)

def end_waiting():
    gameState['iterator'] += 1
    for p in players:
        p["done"] = False
    gameState['done'] = 0
    refresh_all_pages()

def check_action_allowed(player, gameNb):
    if player["done"]: return render_template("en_attente.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], done=gameState['done'], user=player, players=players, background=pages[gameState['iterator']]['background'])
    if pages[gameState['iterator']]['round'][0] != gameNb: return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, page=pages[gameState['iterator']], gameState=gameState, background=pages[gameState['iterator']]['background'])
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
        players[lotteryWinnerID]['gain_a_partager'] = prize
        players[lotteryWinnerID]["message"] = Markup("Vous avez gagné la lotterie ! <br> Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin">')
        log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Le gagnant de la lotterie est " + players[lotteryWinnerID]["name"] + " qui a reçu " + str(prize) + " Pièces")
        if pages[gameState['iterator']]['round'][1] == 3:
            players[lotteryWinnerID]["stars"] += pages[gameState['iterator']]["stars"]
            players[lotteryWinnerID]["message"] = Markup("Vous avez gagné la lotterie ! <br> Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin">.<br>En plus vous recevez ' + str(pages[gameState['iterator']]["stars"]) + ' <i class="fa fa-star"></i> car vous avez remporté la dernière manche.')
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[lotteryWinnerID]["name"] + " a recu " + str(pages[gameState['iterator']]["stars"]) + " étoile(s) car iel a gagné la dernière manche")
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
            player['gain_a_partager'] = prize
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a remporté " + str(prize) + "Pièces")
            for p in players:
                p["message"] = Markup(player["name"] + " a gagné et a remporté " + str(prize) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin">')
            if pages[gameState['iterator']]['round'][1] == 3:
                player["stars"] += pages[gameState['iterator']]["stars"]
                for p in players:
                    p["message"] = Markup(player["name"] + " a gagné et a remporté " + str(prize) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin">.<br> En plus iel recoit ' + str(pages[gameState['iterator']]["stars"]) + ' <i class="fa fa-star"></i> car iel a remporté la dernière manche.')
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a recu " + str(pages[gameState['iterator']]["stars"]) + " étoile(s) car iel a gagné la dernière manche")
            break
    else:
        log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Personne n'a remporté de lot a cette manche")
        for p in players: # initialiser les messages
            p["message"] = "Personne n'a remporté de lot a cette manche"


def game3_init():
    sum = 0
    for p in players:
        p["saved_flouze"] = max(0, p["flouze" ]- pages[gameState['iterator']]['initial_flouze'])
        sum += p["saved_flouze"]
        p["flouze"] = pages[gameState['iterator']]['initial_flouze']
    if sum > 1500:
        gameState['sabotage'] = True
    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "L'argent des joueurs à été mis de coté. Ils leur restent tous " + str(pages[gameState['iterator']]['initial_flouze']) + " Pièces")

def game3_logic():
    assert check_all_done()
    pot_commun = 0
    pot_commun = sum(p["choix"] for p in players)
    if gameState['sabotage']:
        mises = [p['choix'] for p in players]
        pot_commun = 1.2 * np.max(mises)
        log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Cette manche a été sabotée car les participans on été trop coopératifs. Le contenu du pot commun avant l'ajout de la banque à été fixé à " + str(pot_commun))
    prize = int(pot_commun * pages[gameState['iterator']]["gain"] // 5)
    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + str(prize*5) + " Pièces ont été redistribué équitablement à tous les joueurs ce qui fait " + str(prize) + " Pièces par joueur")
    for p in players:
        p["flouze"] += prize
        p["message"] = Markup("Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin">')
    if pages[gameState['iterator']]['round'][1] == 3:
        flouzes = [p['flouze'] for p in players]
        starWinnerID = np.argmax(flouzes)
        if flouzes.count(max(flouzes)) == 1:
            players[starWinnerID]['stars'] += pages[gameState['iterator']]["stars"]
            players[starWinnerID]['message'] = Markup("Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin">.<br>En plus vous recevez ' + str(pages[gameState['iterator']]["stars"]) + " <i class='fa fa-star'></i> car vous avez gagné le plus d'argent durant ce jeu.")
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[starWinnerID]['name'] + " a recu " + str(pages[gameState['iterator']]["stars"]) + " étoile(s) car iel a gagné le plus d'argent durant ce jeu")
        else:
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Dû à une égalité aucune étoile n'a été distribuée")

>>>>>>> 2e508b48b69e3c948e7591fe70516b60a9ea5fcb

from . import engine
from .html_icons import icons

views = Blueprint("views", __name__)

<<<<<<< HEAD
=======
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
                player['gain_a_partager'] = prize
                player["message"] = Markup("Vous avez remporté le prix : " + str(prize) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin">')
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a remporté " + str(prize) + " Pièces")
    if uniqueChoices == 5:
        if pages[gameState['iterator']]['round'][1] == 3:
            gameState["masterPrizeBonus"] = True
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + f"Tous les joueurs ont choisis un prix différent donc le gros lot passe de {pages_by_round[(5, 0)]['prize']} à {pages_by_round[(5, 0)]['prize'] + pages_by_round[(5, 0)]['bonus']} Pièces")
        else:
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Tous les joueurs ont choisis un prix différent donc un bonus s'applique pour la manche suivante")
            gameState["game4_bonus"] += 1


def game5_init():
    for p in gameState['otherPlayers']:
        p['message'] = f"Veuillez attendre la nouvelle proposition de {gameState['starMaster']['name']} ..."
    op = gameState['otherPlayers'].copy()
    op.remove(gameState['otherPlayers'][0])
    for i in range(3):
        op[i]['question'] = quiz[0][i]

def game5_done():
    gameState['iterator'] = len(pages) - 1
    for p in players:
        p["done"] = False
    gameState['done'] = 0
    refresh_all_pages()

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
                if pages[gameState['iterator']]['url'] == "Jeu2-reveal.html":
                    game2_logic()
                if pages[gameState['iterator']]['url'] == "Jeu4-reveal.html":
                    game4_logic()
                if pages[gameState['iterator']]['url'] == "results.html":
                    for p in players: #reinitialiser le statut et les choix des joueurs
                        p["choix"] = None
                        p["gain_a_partager"] = 0
                        p["reveal"] = False
                if pages[gameState['iterator']]['url'] == "title.html":
                    gameState["frameId"] = 0
                gameState['iterator'] += 1
                log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Passage à la page suivante : " + pages[gameState['iterator']]['url'] + " (jeu " + str(pages[gameState['iterator']]['round'][0]) + ", manche " + str(pages[gameState['iterator']]['round'][1]) + ")")

                if pages[gameState['iterator']]['round'] == [3, 0]: #mettre de coté le Flouze
                    game3_init()
                if pages[gameState['iterator']]['round'] == [4, 0]: #rassembler le Flouze
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
>>>>>>> 2e508b48b69e3c948e7591fe70516b60a9ea5fcb


@views.route("/", methods=["GET", "POST"])
def home():
  if "ID" not in session :
    return redirect(url_for("auth.login"))

  game = engine.current_game
  if session["ID"] == "admin":
    if request.method == "POST":
      assert "boutton" in request.form and request.form["boutton"] in ["page suivante", "page précedente"] or\
           "reveal" in request.form and request.form["reveal"] in map(str, range(5)) or\
           "diapo" in request.form and request.form["diapo"] in ["suivant", "précedent"]
      if "reveal" in request.form:
        game.reveal_card(int(request.form["reveal"]))
      elif "diapo" in request.form:
        if request.form["diapo"] == "suivant":
          game.next_frame()
        if request.form["diapo"] == "précedent":
          game.previous_frame()
      elif request.form["boutton"] == "page suivante" and engine.iterator < len(engine.pages)-1:
        if engine.current_page["url"] == "results.html":
          for player in engine.players:
            player.last_profit = 0

        engine.next_page()
        engine.save_data()
        engine.refresh_all_pages()

      elif request.form["boutton"] == "page précedente" and engine.iterator:
        game.next_frame()
        return render_template("monitoring.html" , players=players, pages=pages, gameState=gameState, log=log, imax=min(len(log),20))

<<<<<<< HEAD
        for p in players:
          p["choix"] = False
          p["done"] = False
        gameState["done"] = 0
        engine.iterator -= 1
        engine.log(f"Retour à la page précedente : {engine.current_page['url']} (jeu {engine.current_stage[0]}, manche {engine.current_stage[1]})")
        save_data()
        refresh_all_pages()

    return render_template("monitoring.html" , players=players, pages=pages, gameState=gameState, log=log, imax=min(len(engine.logs),20))

  assert session["ID"] in map(str, range(5))
  player = engine.players[session["ID"]]
  if request.method == "GET":
    if request.form["boutton"] == "partager":
      return render_template("partager.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])

    if request.form["boutton"] == "don":
      return render_template("faire_un_don.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])

    if request.form["boutton"] == "en fait non":
      return render_template(engine.current_page["url"], theme_color=game.config["theme_colors"][0], secondary_theme_color=game.config["theme_colors"][1], user=player, players=players, page=engine.current_page, gameState=gameState, background=game.config["background"])

    if request.form["boutton"] == "léguer etoiles":
      return render_template("don_etoiles.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])

  if request.method == "POST":
    if request.form["boutton"] == "envoyer don":
      receiver_level = request.form.get("destinataire")
      if receiver_level == None:
        flash("Veuillez choisir un destinataire !", category="error")
        return render_template("faire_un_don.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      amount = request.form.get("montant")
      if amount == "":
        flash("Veuiller indiquer un montant !", category="error")
        return render_template("faire_un_don.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      receiver_level = int(receiver_level)
      receiver = engine.players[receiver_level]
      amount = int(amount)
      if amount <= 0:
        flash("Le montant à envoyer ne peut pas être negatif ou nul !", category="error")
        return render_template("faire_un_don.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      if amount > player.flouze:
        flash("Le montant indiqué dépasse votre solde !", category="error")
        return render_template("faire_un_don.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      player.send_money(receiver, amount)
      return render_template(engine.current_page["url"], theme_color=game.config["theme_colors"][0], user=player, players=players, page=engine.current_page, gameState=gameState, background=game.config["background"])

    if request.form["boutton"] == "envoi partager":
      amounts = []
      for receiver in player.other_players:
        amount = request.form.get(receiver["name"])
        amount = 0 if amount == "" else int(amount)
        if amount < 0:
          flash("Vous ne pouvez pas envoiyer des montants négatifs !", category="error")
          return render_template("partager.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
        amounts.append(amount)
      if sum(amounts) > player.last_profit:
        flash("Vous ne pouvez pas donner plus que ce que vous avez reçu !", category="error")
        return render_template("partager.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      if sum(amounts) > player.last_profit:
        flash("Vous ne pouvez pas donner plus que ce que vous avez avez !", category="error")
        return render_template("partager.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      player.last_profit = 0
      player.share_profit(amounts)
      return render_template(engine.current_page["url"], theme_color=game.config["theme_colors"][0], user=player, players=players, page=engine.current_page, gameState=gameState, background=game.config["background"])

    if request.form["boutton"] == "envoyer etoile":
      receiver_level = request.form.get("destinataire")
      amount = request.form.get("quantité")
      if receiver_level == None:
        flash("Veuiller choisir un destinataire !", category="error")
        return render_template("don_etoiles.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      if amount == "":
        flash("Veuiller indiquer un nombre d'étoiles !", category="error")
        return render_template("don_etoiles.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      receiver_level = int(receiver_level)
      amount = int(amount)
      if amount <= 0:
        flash("Le nombre d'étoiles à envoyer ne peut pas être negatif ou nul", category="error")
        return render_template("don_etoiles.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      if amount > player.stars:
        flash("Vous n'avez pas assez d'étoiles", category="error")
        return render_template("don_etoiles.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      receiver = player.other_players[receiver_level]
      player.send_stars(receiver, amount)
      return render_template("don_etoiles.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])

    if request.form["boutton"] == "jeu1-choix":
      action = check_action_allowed(player, 1)
      if action: return action
      tickets = request.form.get("tickets")
      if tickets == None:
        flash("Veuiller faire un choix !", category="error")
        return render_template(engine.current_page["url"], theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      player.choice = int(tickets)
      player.is_done = True
      engine.log(f"{player.name} a choisis {tickets} tickets.")
      flash(f"Vous avez choisis {tickets} tickets.", category="success")
      engine.save_data()

    if engine.current_page["url"] == "Jeu2-choix.html":
      action = check_action_allowed(player, 2)
      if action: return action
      if request.form["boutton"] == "validate num":
        if player.choice == None:
          flash("Veuiller choisir un nombre !", category="error")
          return render_template(engine.current_page["url"], theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
        player.done = True
        engine.log(f"{player.name} a choisis le nombre {player.choice}.")
        flash(f"Vous avez choisis le nombre {player.choice}.", category="success")
        engine.save_data()
      else:
        player.choice = int(request.form["boutton"])

    if request.form["boutton"] == "Jeu3-choix":
      action = check_action_allowed(player, 3)
      if action: return action
      amount = request.form.get("montant")
      if amount == "":
        flash(Markup("Veuiller indiquer un montant<br>(0 si vous ne voulez rien investir) !"), category="error")
        return render_template(engine.current_page["url"], theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      amount = int(amount)
      if amount < 0:
        flash("Le montant à investir ne peut pas être negatif !", category="error")
        return render_template(engine.current_page["url"], theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      if amount > player.flouze:
        flash("Le montant indiqué dépasse votre solde !", category="error")
        return render_template(engine.current_page["url"], theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
      player.flouze -= amount
      player.choice = amount
      player.done = True
      engine.log(f"{player.name} a versé {amount} Pièces dans le pot commun")
      flash(Markup(f"Vous avez versé {amount} {icons['coin']} dans le pot commun"), category="success")
      engine.save_data()

    if engine.current_page["url"] == "Jeu4-choix.html":
      action = check_action_allowed(player, 4)
      if action: return action
      if request.form["boutton"] == "Jeu4-choix":
        if player.choice == None:
          flash("Veuiller choisir un nombre !", category="error")
          return render_template(engine.current_page["url"], theme_color=game.config["theme_colors"][0], user=player, players=players, page=engine.current_page, gameState=gameState, background=game.config["background"])
        player.is_done = True
        prizes = game.config["prize"][game.bonuses]
        prize = prizes[player.choice]
        if prize[player.choice] == "star":
          engine.log(f"{player.name} a choisis l'etoile.")
          flash(Markup(f"Vous avez choisis le prix : {icons['star']}"), category="success")
        else:
          engine.log(f"{player.name} a choisis le prix : {prize} Pièces")
          flash(Markup(f"Vous avez choisis le prix : {prize} {icons['coin']}"), category="success")
        engine.save_data()
      else:
        player.choice = int(request.form["boutton"])





    if request.form["boutton"] == "terminer":
      game.done_stars[player.ID] = True
      if all(game.done_stars[player.ID]):
        engine.next_page()
      engine.save_data()

    if engine.current_page['url'] == "Jeu 5":
      if request.form["boutton"] == 'quiz':
        answer = request.form.get("réponse")
        engine.log(f'{player.name} a donner la réponse {answer} au quiz')


      if request.form["boutton"] == 'proposition':
        total = 0
        for player in game.other_players:
          amount = request.form.get(player.name)
          if amount == "":
            flash("Veuiller indiquer un montant pour tous les joueurs !", category="error")
            return render_template("Jeu5-proposition.html", theme_color=game.config["theme_colors"][0], user=player, otherPlayers=gameState.other_players, background=game.config["background"])
          amount = int(amount)
          total += amount
        if total > player.flouze:
          flash("Les propositions que vous avez faites dépasse vos moyens !", category="error")
          return render_template("Jeu5-proposition.html", theme_color=game.config["theme_colors"][0], user=player, otherPlayers=gameState.other_players, background=game.config["background"])
        for i, player in enumerate(game.other_players):
          amount = int(request.form.get(player.name))
          amount = int(amount)
          game.current_proposition[i] = amount
          player.message = Markup(f"{player.name} vous fait une proposition de {amount} {icons['coin']}")

        engine.next_page()


      elif request.form["boutton"] in ["0", "1"]:
        if player.is_done: pass
        player.choice = int(request.form["boutton"])
        player.is_done = True
      elif request.form["boutton"] == 'nouvelle proposition':
        engine.next_page()
      engine.save_data()

  if engine.current_page['url'] == "Jeu 5":
    if player.is_done:
      return render_template("en_attente_jeu5.html", theme_color=game.config["theme_colors"][0], done=gameState['done'], user=player, players=players, background=game.config["background"])

    if engine.current_page["phase"] == "proposition":
      if player == game.master:
        return render_template("Jeu5-proposition.html", theme_color=game.config["theme_colors"][0], user=player, otherPlayers=gameState.other_players, background=game.config["background"])
      elif game.current_round_id == 0 and game.question_id < 4:
        if player == game.current_guesser:
          return render_template("quiz.html", theme_color=game.config["theme_colors"][0], secondary_theme_color=game.config["theme_colors"][1], user=player, background=game.config["background"], input=True)
        else:
          return render_template("quiz.html", theme_color=game.config["theme_colors"][0], secondary_theme_color=game.config["theme_colors"][1], user=player, background=game.config["background"], input=False)
      else:
        return render_template("results.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])
    elif engine.current_page["phase"] == "validation":
      if player == game.master:
        return render_template("en_attente_jeu5.html", theme_color=game.config["theme_colors"][0], user=player, done=gameState['done'], background=game.config["background"])
      else:
        return render_template("Jeu5-Valider.html", theme_color=game.config["theme_colors"][0], user=player, background=game.config["background"])
    elif engine.current_page["phase"] == "reveal":
      if player == game.master:
        return render_template("Jeu5-reveal.html", theme_color=game.config["theme_colors"][0], user=player, otherPlayers=gameState.other_players, background=game.config["background"])
      else:
        return render_template("results.html", theme_color=game.config["theme_colors"][0], user=player, players=players, background=game.config["background"])

  if player.is_done:
    return render_template("en_attente.html", theme_color=game.config["theme_colors"][0], done=gameState['done'], user=player, players=players, background=game.config["background"])

  return render_template(engine.current_page['url'], theme_color=game.config["theme_colors"][0], secondary_theme_color=game.config["theme_colors"][1], user=player, players=players, page=engine.current_page, gameState=gameState, background=game.config["background"])
=======
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
            player["flouze"] -= montant
            otherPlayers = player['otherPlayers']
            receiver = otherPlayers[receiver_level]
            receiver["flouze"] += montant
            update_data([("flouze", receiver["flouze"])], [receiver])
            send_message(f'Vous avez reçu {montant} <img src="/static/images/coin.png" class="coin-small" alt="Coin"> &nbsp;  de la part de {player["name"]}.', receiver);
            flash(Markup('Vous avez envoyé ' + str(montant) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin"> &nbsp; à ' + receiver["name"]), category='success')
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a fait un don de " + str(montant) + " Pièces à " + receiver["name"])
            save_data()
            return render_template(pages[gameState['iterator']]['url'], theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, page=pages[gameState['iterator']], gameState=gameState, background=pages[gameState['iterator']]['background'])

        if request.form['boutton'] == "envoi partager":
            montants = []
            for receiver in player['otherPlayers']:
                montant = request.form.get(receiver['name'])
                montant = 0 if montant == '' else int(montant)
                if montant < 0:
                    flash('Vous ne pouvez pas envoiyer des montants négatifs', category='error')
                    return render_template("partager.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
                montants.append(montant)
            if sum(montants) > player["gain_a_partager"]:
                flash('Vous ne pouvez pas donner plus que ce que vous avez reçu', category='error')
                return render_template("partager.html", theme_color=theme_colors[pages[gameState['iterator']]['background']][0], user=player, players=players, background=pages[gameState['iterator']]['background'])
            player["gain_a_partager"] = 0
            for receiver, montant in zip(player['otherPlayers'], montants):
                if montant != 0:
                    player["flouze"] -= montant
                    receiver["flouze"] += montant
                    update_data([("flouze", receiver["flouze"])], [receiver])
                    send_message(f'Vous avez reçu {montant} <img src="/static/images/coin.png" class="coin-small" alt="Coin"> &nbsp;  de la part de {player["name"]}.', receiver);
                    flash(Markup('Vous avez envoyé ' + str(montant) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin"> &nbsp; à ' + receiver["name"]), category='success')
                    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a fait un don de " + str(montant) + " Pièces à " + receiver["name"])
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
            flash(Markup('Vous avez versé ' + str(montant) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin"> dans le pot commun'), category='success')
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
                    flash(Markup('Vous avez choisis le prix : ' + str(prize[player["choix"]]) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin">'), category='success')
                if gameState['done'] < 5:
                    update_waiting_count(gameState["done"], 5)
                else:
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
            player["stars"] -= montant
            otherPlayers = player['otherPlayers']
            receiver = otherPlayers[receiver_level]
            receiver["stars"] += montant
            update_data([(f"player{player['ID']}_star", f" {player['stars']}"),
                         (f"player{receiver['ID']}_star", f" {receiver['stars']}")]);
            send_message(f'Vous avez reçu {montant} <i class="fa fa-star"></i> de la part de {player["name"]}.', receiver);
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a légué une étoile à " + receiver["name"])
            flash(Markup('Vous avez envoyé ' + str(montant) + ' <i class="fa fa-star"></i> à ' + receiver["name"]), category='success')
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
                    p["message"] = Markup(player['name'] + ' vous fait une proposition de ' + str(montant) + ' <img src="/static/images/coin.png" class="coin-small" alt="Coin">')
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
                        gameState['starMaster']['message'] = Markup(f"Votre proposition a été acceptée par la majorité.<br>Vous repartez donc avec {gameState['starMaster']['flouze']} <img src='/static/images/coin.png' style='width:20px' alt='Coin'> ce qui correspond à {gameState['starMaster']['flouze']/10} €")
                        for p in gameState['otherPlayers']:
                            gameState['starMaster']['flouze'] -= p['proposition']
                            p['flouze'] += p['proposition']
                            p['message'] = Markup(f"La proposition à été acceptée par la majorité des joueurs.<br>Vous avez recu {p['proposition']} <img src='/static/images/coin.png' style='width:20px' alt='Coin'> de {gameState['starMaster']['name']} <br>Vous repartez donc avec {gameState['starMaster']['flouze']} <img src='/static/images/coin.png' style='width:20px' alt='Coin'> ce qui correspond à {gameState['starMaster']['flouze']/10} €")
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
                                p['message'] = Markup(f"La proposition à été refusée par au moins 2 joueurs.<br>En attente d'une nouvelle proposition.")
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
>>>>>>> 2e508b48b69e3c948e7591fe70516b60a9ea5fcb
