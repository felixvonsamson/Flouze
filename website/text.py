color_names = [
    "bleu",
    "rouge",
    "jaune",
    "verte",
    "violette"
]

game_names = [
    "La Lotterie",
    "L'enchère inversée",
    "Le pot commun",
    "Le con promis",
    "Le bras de fer"
]

quiz = [
  (["_______ _______ _ a-t-il __ __ drapeau ______ ?", 
    "_______ d’étoiles _ ____ sur __ ______ valaisan ?", 
    "Combien _______ y ____ __ le _______ ______ ?"], 
   ["Combien d'étoiles y a-t-il sur le drapeau valaisan ?", 
   "13"]), 
  (["Quel ____ __ enclavé ____ le _______ ?", 
    "___ pays ___ ______ dans __ _______ ?", 
    "___ ____ est ______ ____ __ Sénégal ?"], 
   ["Quel pays est enclavé dans le Sénégal ?", 
    "La Gambie"]), 
  (["Combien _ ___ de _____ __ tram _ ________ ?", 
    "_______ y ___ __ lignes __ ____ à ________ ?", 
    "_______ _ a-t-il __ ____ de ____ _ Bordeaux ?"], 
   ["Combien y a-t-il de lignes de tram à Bordeaux ?", 
    "4"]), 
  (["Quel ____ ___ pseudo ___ ____ of ____ ?", 
    "____ était ___ ______ sur ____ __ clans ?", 
    "____ ____ mon _____ ___ clash __ ____ ?"], 
   ["Quel était mon pseudo sur clash of clans ?", 
    "FvS"]), 
  (["Quel __ __ nom __ _____ de ____ __ la ______ ______ LTT ?", 
    "____ est __ ___ de _____ __ Linus, __ __ chaine ______ ___ ?", 
    "____ __ le ___ __ famille __ ____ de __ ______ Youtube ___ ?"], 
   ["Quel est le nom de famille de Linus, de la chaine LTT ?", 
    "Sebastian"])
]

logs = [
  "LE JEU A COMMENCÉ !",
  "Saut à la page : {page} (jeu {jeu}, manche {manche})",
  "Retour à la page précédante : {page} (jeu {jeu}, manche {manche})",
  "Passage passif à la page suivante : {page} (jeu {jeu}, manche {manche})",
  "Passage à la page suivante : {page} (jeu {jeu}, manche {manche})",
  "{name} s'est connecté.",
  "{name} a choisi la couleur {color}.",
  "{name} a fait un don de {amount} Pièces à {receiver}.",
  "{name} réclame {amount} Pièces de la part de {donor}.",
  "{name} a légué {stars} étoile(s) à {receiver}.",
  "{name} a choisi {tickets} ticket(s).",
  "Le gagnant de la loterie est {name} qui a reçu {prize} Pièces.",
  "{name} a reçu {stars} étoile(s) car iel a gagné la dernière manche.",
  "Il n'y a pas de gagnant à la loterie car personne n'a participé.",
  "{name} a choisi le nombre {number}.",
  "{name} a remporté {prize} Pièces.",
  "{name} a reçu {stars} étoile(s) car iel a gagné la dernière manche.",
  "Personne n'a gagné à cette manche.",
  "L'argent des joueurs à été mis de coté. Ils leur restent tous {flouze} Pièces.",
  "{name} a versé {amount} Pièces dans le pot commun.",
  "Cette manche a été sabotée car les participans ont été trop coopératifs. Le contenu du pot commun avant l'ajout de la banque à été fixé à {common_pot}.",
  "{total} Pièces ont été redistribuées équitablement à tous les joueurs ce qui fait {prize} Pièces par joueur.",
  "Les gains bruts sont de : {benefit}.",
  "{name} a reçu {stars} étoile(s) car iel a gagné le plus d'argent durant ce jeu.",
  "Dû à une égalité, aucune étoile n'a été distribuée.",
  "L'argent mis de coté a été remis en jeu.",
  "{name} a choisi la deuxième étoile.",
  "{name} a choisi l'étoile.",
  "{name} a choisi le prix : {prize} Pièces.",
  "{name} a gagné une étoile.",
  "{name} a remporté {prize} Pièces.",
  "Tous les joueurs ont choisi un prix différent donc un bonus s'applique pour la manche suivante.",
  "Tous les joueurs ont choisi un prix différent donc le gros lot passe de {prize} à {bonus} Pièces.",
  "Le nombre d'étoiles pour chaque joueur est respectivement : {stars}.",
  "{name} a le plus d'étoiles et remporte ainsi la somme de {jackpot} Pièces pour le cinquième jeu.",
  "Dû à l'égalité d'étoiles, personne ne remporte le gros lot et le cinquième jeu est annulé.",
  "{name} a donné la réponse {answer} à la question : '{question}'.",
  "La réponse a été validée.",
  "{gamemaster} a proposé {amount} Pièces à {name}.",
  "{name} a {decision} la proposition de {gamemaster}.",
  "La proposition a été acceptée par la majorité.",
  "La proposition n'a pas été acceptée par la majorité. Les {jackpot} Pièces sont retirées à {name}.",
  "La proposition n'a pas été acceptée par la majorité.",
  "{name} repart avec {flouze} Pièces, ce qui correspond à {euros} €.",
  "FIN DU JEU"
]

sentences = {
  "incorect password" : [
    "Mot de passe incorrect, réessayez."],
  "not recognized" : [
    "Vous n'êtes pas un participant."],
  "connected" : [
    "Vous êtes connecté !"],
  "color selected" : [
    "Vous avez choisi la couleur {color}."],
  "color already selected" : [
    "Vous avez déjà sélectionné cette couleur."],
  "color not avalable" : [
    "{name} a été plus rapide que vous !"],
  "sent flouze" : [
    "Vous avez envoyé {amount} {coin} à {name}."],
  "sent stars" : [
    "Vous avez envoyé {stars} {star} à {name}."],
  "received flouze" : [
    "Vous avez reçu {amount} {coin} de la part de {name}."],
  "received stars" : [
    "Vous avez reçu {stars} {star} de la part de {name}."],
  "flouze claim" : [
    "{name} vous réclame {amount} {coin}."],
  "not enough money for flouze claim" : [
    "{name} vous réclame {amount} {coin} mais vous n'avez pas cette somme !"],
  "claim can't be accepted" : [
    "{name} ne peut pas accepter votre proposition car iel n'a pas assez d'argent !"],
  "claim rejected" : [
    "Votre demande à été refusée par {name}."],
  "not enough money" : [
    "Le montant indiqué dépasse votre solde !"],
  "please use donation" : [
    "Si vous voulez donner de l'argent veuillez utiliser le boutton 'Faire un don'..."],
  "claim too high" : [
    "Vous ne pouvez pas réclamer plus que ce que vous avez perdu !"],
  "donation too high" : [
    "Vous ne pouvez pas donner plus que ce que vous avez reçu !"],
  "not enough money for donation" : [
    "Vous ne pouvez pas donner plus que ce que vous avez !"],
  "not enough stars" : [
    "Vous n'avez pas assez d'étoiles."],
  "not enough money for offer" : [
    "Les propositions que vous avez faites dépasse vos moyens !"],
  "chosen tickets" : [
    "Vous avez choisi {tickets} ticket(s)."],
  "lottery looser" : [
    "Vous n'avez pas gagné la loterie ! {smiley}"],
  "lottery winner" : [
    "Vous avez gagné la loterie !<br>Vous avez reçu {prize} {coin} !"],
  "last round winner" : [
    "<br>En plus vous recevez {stars} {star} car vous avez remporté la dernière manche."],
  "chosen number" : [
    "Vous avez choisi le nombre {number}."],
  "winner number" : [
    "Vous avez gagné et remportez {prize} {coin}."],
  "looser number" : [
    "Vous n'avez pas gagné."],
  "no winner" : [
    "Personne n'a gagné à cette manche."],
  "flouze invested" : [
    "Vous avez versé {amount} {coin} dans le pot commun."],
  "return on investment" : [
    "Vous avez reçu {prize} {coin}."],
  "made the most money" : [
    "Vous avez reçu {prize} {coin}.<br>En plus vous recevez {stars} {star} car vous avez gagné le plus d'argent durant ce jeu."],
  "chosen star" : [
    "Vous avez choisi le prix : {star}."],
  "chosen prize" : [
    "Vous avez choisi le prix : {prize} {coin}."],
  "won star" : [
    "Vous avez remporté le prix : {star}."],
  "won prize" : [
    "Vous avez remporté le prix {prize} {coin}."],
  "prize not won" : [
    "Vous n'avez pas remporté le prix."],
  "starmaster announcement" : [
    "{name} a le plus d'étoiles et est ainsi en possesion de la somme de {jackpot} {coin} pour le 5ème jeu."],
  "you are the starmaster" : [
    "Vous avez le plus d'étoiles et êtes ainsi en possesion de la somme de {jackpot} {coin} pour le 5ème jeu."],
  "tie" : [
    "Dû à l'égalité d'étoiles, personne ne remporte le gros lot et le cinquième jeu est annulé."],
  "wrong awnser" : [
    "Perdu ! La bonne réponse à la question '{question}' était : {correct_answer}"],
  "right awnser" : [
    "Félicitation ! Vous remportez {prize} {coin} !"],
  "wait" : [
    "Veuillez attendre la proposition de {name} ..."],
  "offer" : [
    "{name} vous fait une proposition de {amount} {coin}."],
  "your offer is accepted" : [
    "Votre proposition a été acceptée par la majorité."],
  "offer accepted" : [
    "La proposition à été acceptée par la majorité des joueurs."],
  "offer received" : [
    "<br>Vous avez reçu {offer} {coin} de {name}."],
  "lost flouze" : [
    "<br>Vous vous êtes fait racketter {los} {coin} par {name}."],
  "your last offer is declined" : [
    "Votre dernière proposition n'a pas été acceptée par la majorité. Les {jackpot} {coin} vous sont donc retirés."],
  "last offer declined" : [
    "Aucun accord n'a été trouvé après ces 3 essais donc {name} ne remporte pas les {jackpot} {coin}."],
  "your offer is declined" : [
    "Votre proposition n'a pas été acceptée par la majorité !"],
  "offer declined" : [
    "La proposition à été refusée par au moins 2 joueurs.<br>En attente d'une nouvelle proposition..."],
  "final earnings" : [
    "<br>Vous repartez donc avec {flouze} {coin}, ce qui correspond à {euros} €."]
}

html = [
  "Login",
  "Qui est-tu ?",
  "Prénom",
  "Mot de passe",
  "Se connecter",
  "Flouze - Jeu 1",
  "Flouze - Jeu 2",
  "Flouze - Jeu 3",
  "Flouze - Jeu 4",
  "Flouze - Jeu 5",
  "Flouze FIN",
  "QUIZ",
  "Résultats",
  "Faire un don",
  "Partager",
  "à partager",
  "Votre demande peut être refusée par les joueurs",
  "Bienvenue",
  "Couleurs",
  "Donner des étoiles ?",
  "Souhaitez-vous donner des étoiles ?",
  "OUI",
  "NON",
  "Donner des étoiles",
  "À qui souhaitez-vous donner des étoiles ?",
  "Envoyer",
  "Retour",
  "en fait non",
  "Valider",
  "En attente des autres joueurs...",
  "Destinataire",
  "Combien de tickets voulez-vous mettre en jeu ?",
  "Nombre de tickets",
  "Aucun ticket",
  "1 ticket",
  "tickets",
  "Choisissez un nombre :",
  "Combien souhaitez-vous investir ?",
  "Choisissez un lot :",
  "Veuillez faire une offre aux autres joueurs :",
  "Faire une proposition",
  "Refusé",
  "Accepté",
  "Refuser",
  "Accepter",
  "Faire une nouvelle proposition"
]