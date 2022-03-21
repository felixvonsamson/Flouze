import random
import numpy as np
from abc import ABC, abstractmethod

class Game(ABC):
    @abstractmethod
    def game(self):
        pass

    @abstractmethod
    def logic(self):
        pass

class Game1(Game):
    def __init__():
        pass

    def logic(self)


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
        players[lotteryWinnerID]["message"] = Markup("Vous avez gagné la lotterie ! <br> Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" style="width:25px" alt="Coin">')
        log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Le gagnant de la lotterie est " + players[lotteryWinnerID]["name"] + " qui a reçu " + str(prize) + " Pièces")
        if pages[gameState['iterator']]['round'][1] == 3:
            players[lotteryWinnerID]["stars"] += pages[gameState['iterator']]["stars"]
            players[lotteryWinnerID]["message"] = Markup("Vous avez gagné la lotterie ! <br> Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" style="width:25px" alt="Coin">.<br>En plus vous recevez ' + str(pages[gameState['iterator']]["stars"]) + ' <i class="fa fa-star"></i> car vous avez remporté la dernière manche.')
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[lotteryWinnerID]["name"] + " a recu " + str(pages[gameState['iterator']]["stars"]) + " étoile(s) car iel a gagné la dernière manche")
    else:
        log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Il n'y a pas de gagnant à la lotterie car personne n'a participé")


def game2_logic():
    assert check_all_done()
    for i in range(1, 6):
        count = 0 # nombre  de fois que i a été choisis
        player = None
        for p in players:
            if p["choix"] == i:
                count += 1
                player = p # joueur gagnant
        if count == 1:
            prize = pages[gameState['iterator']]["prize"]*i
            player["flouze"] += prize
            player['gain_a_partager'] = prize
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + player["name"] + " a remporté " + str(prize) + "Pièces")
            for p in players:
                p["message"] = Markup(player["name"] + " a gagné et a remporté " + str(prize) + ' <img src="/static/images/coin.png" style="width:22px" alt="Coin">')
            if pages[gameState['iterator']]['round'][1] == 3:
                player["stars"] += pages[gameState['iterator']]["stars"]
                for p in players:
                    p["message"] = Markup(player["name"] + " a gagné et a remporté " + str(prize) + ' <img src="/static/images/coin.png" style="width:22px" alt="Coin">.\n En plus iel recoit ' + str(pages[gameState['iterator']]["stars"]) + ' <i class="fa fa-star"></i> car iel a remporté la dernière manche.')
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
        pot_commun = 1.2 * np.argmax(mises)
        log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Cette manche a été sabotée car les participans on été trop coopératifs. Le contenu du pot commun avant l'ajout de la banque à été fixé à" + str(pot_commun))
    prize = int(pot_commun * pages[gameState['iterator']]["gain"] // 5)
    log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + str(prize*5) + " Pièces ont été redistribué équitablement à tous les joueurs ce qui fait " + str(prize) + " Pièces par joueur")
    for p in players:
        p["flouze"] += prize
        p["message"] = Markup("Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" style="width:22px" alt="Coin">')
    if pages[gameState['iterator']]['round'][1] == 3:
        flouzes = [p['flouze'] for p in players]
        starWinnerID = np.argmax(flouzes)
        if flouzes.count(max(flouzes)) == 1:
            players[starWinnerID]['stars'] += pages[gameState['iterator']]["stars"]
            players[starWinnerID]['message'] = Markup("Vous avez reçu " + str(prize) + ' <img src="/static/images/coin.png" style="width:22px" alt="Coin">.\nEn plus vous recevez ' + str(pages[gameState['iterator']]["stars"]) + " <i class='fa fa-star'></i> car vous avez gagné le plus d'argent durant ce jeu.")
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + players[starWinnerID]['name'] + " a recu " + str(pages[gameState['iterator']]["stars"]) + " étoile(s) car iel a gagné le plus d'argent durant ce jeu")
        else:
            log.append(datetime.datetime.now().strftime('%H:%M:%S : ') + "Dû à une égalité aucune étoile n'a été distribuée")


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
                player['gain_a_partager'] = prize
                player["message"] = Markup("Vous avez remporté le prix : " + str(prize) + ' <img src="/static/images/coin.png" style="width:22px" alt="Coin">')
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