#[0] : English
#[1] : French
#[2] : German

languages_name = ["en", "fr", "de"]

color_names = {
  "blue" : [
    "blue",
    "bleu",
    "blau"],
  "red" : [
    "red",
    "rouge",
    "rot"],
  "yellow" : [
    "yellow",
    "jaune",
    "gelb"],
  "green" : [
    "green",
    "verte",
    "grün"],
  "teal" : [
    "teal",
    "sarcelle",
    "teal"],
  "purple" : [
    "purple",
    "violette",
    "lila"],
  "magenta" : [
    "magenta",
    "magenta",
    "magenta"],
  "orange" : [
    "orange",
    "orange",
    "orange"]
}

game_names = {
    "game 1" : [
      "The lottery",
      "La loterie",
      "Das Lotteriespiel"],
    "game 2" : [
      "The reverse auction",
      "L'enchère inversée",
      "Die Rückwärtsauktion"],
    "game 3" : [
      "The Common Pot",
      "Le pot commun",
      "Der gemeinsame Topf"],
    "game 4" : [
      "The trade-off",
      "Le con promis",
      "Der Kompromiß"],
    "game 5" : [
      "The arm wrestling",
      "Le bras de fer",
      "Die Verhandlung"]
}

quiz = [
  [
    ("Which country is landlocked in Senegal?", "Gambia"),
    ("Quel pays est enclavé dans le Sénégal ?", "La Gambie"),
    ("Welches Land wird von Senegal umschlossen?", "Gambia")],
  [
    ("Who wrote 'The Lord of the Rings'?", "J. R. R. Tolkien"),
    ("Qui est l'auteur du 'Segnieurs des anneaux' ?", "J. R. R. Tolkien"),
    ("Wer hat 'Herr der Ringe' geschrieben ?", "J. R. R. Tolkien")],
  [
    ("What is the derivative of speed?", "acceleration"),
    ("Quel est la dérivée de la vitesse ?", "l'accélération"),
    ("Was ist die Ableitung der Geschwindigkeit ?", "die Beschleunigung")],
  [
    ("In which year did the fall of the Berlin Wall happen?", "1989"),
    ("En quelle année s'est déroulé la chute du mur de Berlin ?", "1989"),
    ("In welchem Jahr ist die Berliner Mauer gefallen ?", "1989")],
  [
    ("Who won the 2018 football world cup?", "France"),
    ("Qui a gagné la coupe du monde de foot 2018 ?", "la France"),
    ("Wer hat die Fußballweltmeisterschaft 2018 gewonne ?", "Frankreich")],
  [
    ("Who is the actor that plays the Warden Supervisor in the moveie 'The Green Mile'?", "Tom Hanks"),
    ("Quel est l'acteur qui joue le gardien-chef dans le film 'La Ligne verte' ?", "Tom Hanks"),
    ("Welcher Schauspieler spielt den Oberaufseher in dem Film 'The Green Mile' ?", "Tom Hanks")],
  [
    ("Which renewable energy is the most used?", "biomass"),
    ("Quelle énergie renouvelable est la plus utilisée ?", "la biomasse"),
    ("Welche erneuerbare Energie wird am häufigsten genutzt ?", "Biomasse")],
  [
    ("Who gave birth to communism?", "Karl Marx"),
    ("Qui a donné naissance au communisme ?", "Karl Marx"),
    ("Wer hat den Kommunismus ins Leben gerufen ?", "Karl Marx")]
]

logs_txt = {
  "start" : [
    "THE GAME HAS BEGUN !",
    "LE JEU A COMMENCÉ !",
    "DAS SPIEL HAT BEGONNEN !"],
  "jump to page" : [
    "Jump to page : {page} (game {jeu}, round {manche})",
    "Saut à la page : {page} (jeu {jeu}, manche {manche})",
    "Sprung zu Seite : {page} (Spiel {jeu}, Runde {manche})"],
  "back to page" : [
    "Back to previous page : {page} (game {jeu}, round {manche})",
    "Retour à la page précédante : {page} (jeu {jeu}, manche {manche})",
    "Zurück zur vorherigen Seite : {page} (Spiel {jeu}, Runde {manche})"],
  "next page passive" : [
    "Going to next page passively : {page} (game {jeu}, round {manche})",
    "Passage passif à la page suivante : {page} (jeu {jeu}, manche {manche})",
    "Passiver Wechsel zur nächsten Seite : {page} (Spiel {jeu}, Runde {manche})"],
  "next page" : [
    "Going to next page : {page} (game {jeu}, round {manche})",
    "Passage à la page suivante : {page} (jeu {jeu}, manche {manche})",
    "Wechsel zur nächsten Seite : {page} (Spiel {jeu}, Runde {manche})"],
  "connected" : [
    "{name} has logged in.",
    "{name} s'est connecté.",
    "{name} hat sich eingeloggt."],
  "color choice" : [
    "{name} chose the color {color}.",
    "{name} a choisi la couleur {color}.",
    "{name} hat die Farbe {color} gewählt"],
  "donation" : [
    "{name} donated {amount} coins to {receiver}.",
    "{name} a fait un don de {amount} Pièces à {receiver}.",
    "{name} hat {receiver} {amount} Münzen gespendet"],
  "claim" : [
    "{name} asks for {name} Coins from {donor}.",
    "{name} réclame {name} Pièces de la part de {donor}.",
    "{name} fordert {name} Münzen von {donor}."],
  "star donation" : [
    "{name} left {stars} star(s) to {receiver}.",
    "{name} a légué {stars} étoile(s) à {receiver}.",
    "{name} hat {receiver} {stars} stern(e) vermacht."],
  "tickets choice" : [
    "{name} chose {tickets} ticket(s).",
    "{name} a choisi {tickets} ticket(s).",
    "{name} hat {tickets} ticket(s) gewählt"],
  "lottery winner" : [
    "The winner of the lottery is {name} who won {prize} coins.",
    "Le gagnant de la loterie est {name} qui a reçu {prize} Pièces.",
    "Der Gewinner der Lotterie ist {name}, der {prize} Münzen erhalten hat."],
  "last round winner" :[
    "{name} has received {stars} star(s) because he/she has won the last round.",
    "{name} a reçu {stars} étoile(s) car iel a gagné la dernière manche.",
    "{name} hat {stars} Stern(e) erhalten da er/sie die letzte Runde gewonne hat."],
  "no lottery winner" : [
    "There is no winner in the lottery because no one participated.",
    "Il n'y a pas de gagnant à la loterie car personne n'a participé.",
    "Es gibt keinen Gewinner in der Lotterie, weil niemand teilgenommen hat"],
  "number choice" : [
    "{name} chose the number {number}.",
    "{name} a choisi le nombre {number}.",
    "{name} hat die Zahl {number} gewählt."],
  "winner number" : [
    "{name} won {prize} coins.",
    "{name} a remporté {prize} Pièces.",
    "{name} hat {prize} Münzen gewonnen."],
  "no winner" : [
    "No one won in this round.",
    "Personne n'a gagné à cette manche.",
    "Niemand hat in dieser Runde gewonnen."],
  "money set aside" : [
    "The players' money has been set aside. They all have {flouze} coins left.",
    "L'argent des joueurs à été mis de coté. Ils leur restent tous {flouze} Pièces.",
    "Das Geld der Spieler wurde beiseitegelegt. Sie haben alle {flouze} Münzen übrig."],
  "investment in common pot" : [
    "{name} contributed {amount} Coins to the common pot.",
    "{name} a versé {amount} Pièces dans le pot commun.",
    "{name} hat {amount} Münzen in den gemeinsamen Topf investiert."],
  "sabotage" : [
    "This round was sabotaged because the participants were too cooperative. The content of the common pot before the bonus was set to {common_pot}.",
    "Cette manche a été sabotée car les participans ont été trop coopératifs. Le contenu du pot commun avant l'ajout de la banque à été fixé à {common_pot}.",
    "Diese Runde wurde sabotiert, weil die Teilnehmer zu kooperativ waren. Der Inhalt des gemeinsamen Topfes, vor Beitrag der Bank, wurde auf {common_pot} festgelegt."],
  "pot distribution" : [
    "{total} Coins have been redistributed equally to all players making {prize} Coins per player.",
    "{total} Pièces ont été redistribuées équitablement à tous les joueurs ce qui fait {prize} Pièces par joueur.",
    "{total} Münzen wurden gleichmäßig an alle Spieler verteilt, was {prize} Münzen pro Spieler ergibt"],
  "benefits" : [
    "The gross earnings are : {benefit}.",
    "Les gains bruts sont de : {benefit}.",
    "Die Bruttogewinne betragen : {benefit}."],
  "largest benefit" : [
    "{name} received {stars} star(s) because she/he won the most money during this game.",
    "{name} a reçu {stars} étoile(s) car iel a gagné le plus d'argent durant ce jeu.",
    "{name} hat {stars} Stern(e) erhalten, weil er/sie während dieses Spiels das meiste Geld gewonnen hat"],
  "no stars" : [
    "No one won the last round so no one is ganging a star.",
    "Personne n'a remporté la dernière manche donc personne ne gange d'étoile.",
    "Niemand hat die letzte Runde gewonnen, also bekommt auch niemand einen Stern."],
  "tie no stars" : [
    "Due to a tie, no stars were awarded.",
    "Dû à une égalité, aucune étoile n'a été distribuée.",
    "Aufgrund eines Unentschiedens wurden keine Sterne verteilt."],  
  "money returned" : [
    "The money set aside has been put back into play.",
    "L'argent mis de coté a été remis en jeu.",
    "Das beiseitegelegte Geld wurde wieder ins Spiel gebracht"],
  "chosen star2" : [
    "{name} chose the second star.",
    "{name} a choisi la deuxième étoile.",
    "{name} hat den zweiten Stern gewählt."],
  "chosen star" : [
    "{name} chose the star.",
    "{name} a choisi l'étoile.",
    "{name} hat den Stern gewählt."],
  "chosen prize" : [
    "{name} chose the prize : {prize} coins.",
    "{name} a choisi le lot : {prize} Pièces.",
    "{name} hat den Los {prize} Münzen gewählt."],
  "won star" : [
    "{name} won a star.",
    "{name} a gagné une étoile.",
    "{name} hat ein Stern gewonnen."],
  "won prize" : [
    "{name} won {prize} coins.",
    "{name} a remporté {prize} Pièces.",
    "{name} hat {prize} gewonnen."],
  "bonus" : [
    "All players have chosen a different prize so a bonus applies for the next round.",
    "Tous les joueurs ont choisi un prix différent donc un bonus s'applique pour la manche suivante.",
    "Alle Spieler haben einen unterschiedlichen Preis gewählt, also gilt ein Bonus für die nächste Runde"],
  "bonus round 3" : [
    "All players have chosen a different prize so the jackpot goes from {prize} to {bonus} coins.",
    "Tous les joueurs ont choisi un prix différent donc le gros lot passe de {prize} à {bonus} Pièces.",
    "Alle Spieler haben einen unterschiedlichen Preis gewählt, also wechselt der Jackpot von {prize} zu {bonus} Münzen."],
  "star count" : [
    "The number of stars for each player is respectively: {stars}.",
    "Le nombre d'étoiles pour chaque joueur est respectivement : {stars}.",
    "Die Anzahl der Sterne für jeden Spieler ist jeweils: {stars}."],
  "most stars" : [
    "{name} has the most stars and thus wins the sum of {jackpot} Coins for the fifth game.",
    "{name} a le plus d'étoiles et remporte ainsi la somme de {jackpot} Pièces pour le cinquième jeu.",
    "{name} hat die meisten Sterne und gewinnt damit die Summe von {jackpot} Münzen für das fünfte Spiel"],
  "tie star" : [
    "Due to the tie of stars, no one wins the jackpot and the fifth game is cancelled.",
    "Dû à l'égalité d'étoiles, personne ne remporte le gros lot et le cinquième jeu est annulé.",
    "Aufgrund der Sternengleichheit gewinnt niemand den Hauptpreis und das fünfte Spiel wird abgebrochen"],
  "awnser proposal" : [
    "{name} gave the answer {answer} to the question : '{question}'.",
    "{name} a donné la réponse {answer} à la question : '{question}'.",
    "{name} hat die Antwort {answer} auf die Frage '{question}' gegeben"],
  "awnser accepted" : [
    "The answer has been validated.",
    "La réponse a été validée.",
    "Die Antwort wurde bestätigt."],
  "awnser refused" : [
    "The answer has been refused.",
    "La réponse a été refusée.",
    "Die Antwort wurde nicht akzeptiert."],
  "gamemaster offer" : [
    "{gamemaster} offered {amount} coins to {name}.",
    "{gamemaster} a proposé {amount} Pièces à {name}.",
    "{gamemaster} hat {name} {amount} Münzen angeboten"],
  "offer decision" : [
    "{name} has {decision} the offer from {gamemaster}.",
    "{name} a {decision} la proposition de {gamemaster}.",
    "{name} hat das Angebot von {gamemaster} {decision}."],
  "offer accepted" : [
    "The offer was accepted by the majority.",
    "L'offre a été acceptée par la majorité.",
    "Das Angebot wurde von der Mehrheit angenommen."],
  "last offer rejected" : [
    "The offer was not accepted by the majority. The {jackpot} coins are withdrawn from {name}.",
    "L'offre n'a pas été acceptée par la majorité. Les {jackpot} Pièces sont retirées à {name}.",
    "Das Angebot wurde von der Mehrheit nicht angenommen. Die {jackpot} Münzen werden {name} zurückgezogen"],
  "offer rejected" : [
    "The offer was not accepted by the majority.",
    "L'offre n'a pas été acceptée par la majorité.",
    "Das Angebot wurde von der Mehrheit nicht angenommen."],
  "final earnings" : [
    "{name} leaves with {flouze} coins.",
    "{name} repart avec {flouze} Pièces.",
    "Das Endvermögen von {name} is {flouze} Münzen."],
  "end" : [
    "END OF THE GAME",
    "FIN DU JEU",
    "SPIELENDE"]
}

player_txt = {
  "incorect password" : [
    "Wrong password, try again.",
    "Mot de passe incorrect, réessayez.",
    "Falsches Passwort, versuchen sie es erneut."],
  "not recognized" : [
    "You're not a participant.",
    "Vous n'êtes pas un participant.",
    "Sie sind kein Teilnehmer."],
  "connected" : [
    "You are logged in !",
    "Vous êtes connecté !",
    "Sie sind eingeloggt !"],
  "language change" : [
    "The language was changed to english.",
    "La langue a été changée en français.",
    "Die Sprache wurde auf Deutsch umgestellt."],
  "color selected" : [
    "You have chosen the color {color}.",
    "Vous avez choisi la couleur {color}.",
    "Sie haben die Farbe {color} gewählt."],
  "color already selected" : [
    "You have already selected this color.",
    "Vous avez déjà sélectionné cette couleur.",
    "Sie haben diese Farbe bereits ausgewählt."],
  "color not avalable" : [
    "{name} was quicker !",
    "{name} a été plus rapide !",
    "{name} war schneller !"],
  "sent flouze" : [
    "You have sent {amount} {coin} to {name}.",
    "Vous avez envoyé {amount} {coin} à {name}.",
    "Sie haben {amount} {coin} an {name} überwiesen."],
  "sent stars" : [
    "You have sent {stars} {star} to {name}.",
    "Vous avez envoyé {stars} {star} à {name}.",
    "Sie haben {stars} {star} an {name} gespended."],
  "received flouze" : [
    "You received {amount} {coin} from {name}.",
    "Vous avez reçu {amount} {coin} de la part de {name}.",
    "Sie haben {amount} {coin} von {name} erhalten."],
  "received stars" : [
    "You received {stars} {star} from {name}.",
    "Vous avez reçu {stars} {star} de la part de {name}.",
    "Sie haben {stars} {star} von {name} erhalten."],
  "flouze claim" : [
    "{name} asks you for {amount} {coin}.",
    "{name} vous réclame {amount} {coin}.",
    "{name} Verlangt von ihnen {amount} {coin}."],
  "not enough money for flouze claim" : [
    "{name} asks you for {amount} {coin} but you don't have this amount.",
    "{name} vous réclame {amount} {coin} mais vous n'avez pas cette somme.",
    "{name} Verlangt von ihnen {amount} {coin}, aber sie haben diesen betrag nicht."],
  "claim can't be accepted" : [
    "{name} cannot accept your offer because she/he does not have enough money.",
    "{name} ne peut pas accepter votre offre car iel n'a pas assez d'argent.",
    "{name} kann Ihren Angebot nicht annehmen, weil er/sie nicht genug Geld hat."],
  "claim rejected" : [
    "Your request has been denied by {name}."
    "Votre demande à été refusée par {name}.",
    "Ihre Anfrage wurde von {name} abgelehnt."],
  "not enough money" : [
    "The amount you entered exceeds your balance !",
    "Le montant indiqué dépasse votre solde !",
    "Der angegebene Betrag übersteigt Ihr Guthaben !"],
  "please use donation" : [
    "If you want to donate money please use the 'Donate' button...",
    "Si vous voulez donner de l'argent veuillez utiliser le boutton 'Faire un don'...",
    "Wenn Sie Geld spenden möchten, verwenden Sie bitte den Button 'Spenden'..."],
  "claim too high" : [
    "You can't claim more than you lost !",
    "Vous ne pouvez pas réclamer plus que ce que vous avez perdu !",
    "Sie können nicht mehr zurückfordern als das, was Sie verloren haben !"],
  "donation too high" : [
    "You can't share more than you've received !",
    "Vous ne pouvez pas partager plus que ce que vous avez reçu !",
    "Sie können nicht mehr teilen als das, was Sie erhalten haben !"],
  "not enough money for donation" : [
    "You can't give more than you have !",
    "Vous ne pouvez pas donner plus que ce que vous avez !",
    "Sie können nicht mehr geben, als Sie haben !"],
  "not enough stars" : [
    "You don't have enough stars.",
    "Vous n'avez pas assez d'étoiles.",
    "Sie haben nicht genug Sterne."],
  "not enough money for offer" : [
    "The offers you have made are beyond your means !",
    "Les offres que vous avez faites dépasse vos moyens !",
    "Die Angebote, die Sie gemacht haben, übersteigen Ihre Mittel !"],
  "chosen tickets" : [
    "You have chosen {tickets} ticket(s).",
    "Vous avez choisi {tickets} ticket(s).",
    "Sie haben {tickets} Ticket(s) gewählt."],
  "lottery looser" : [
    "You didn't win the lottery ! {smiley}",
    "Vous n'avez pas gagné la loterie ! {smiley}",
    "Sie haben die Lotterie nicht gewonnen ! {smiley}"],
  "lottery winner" : [
    "You have won the lottery ! You have received {prize} {coin} !",
    "Vous avez gagné la loterie !<br>Vous avez reçu {prize} {coin} !",
    "Sie haben die Lotterie gewonnen !<br> Sie haben {prize} {coin} erhalten !"],
  "last round winner" : [
    "<br>In addition you get {stars} {star} because you won the last round.",
    "<br>En plus vous recevez {stars} {star} car vous avez remporté la dernière manche.",
    "<br>Außerdem erhalten Sie {stars} {star}, weil Sie die letzte Runde gewonnen haben."],
  "chosen number" : [
    "You have chosen the number {number}.",
    "Vous avez choisi le nombre {number}.",
    "Sie haben die Zahl {number} gewählt."],
  "winner number" : [
    "You have won and get {prize} {coin}.",
    "Vous avez gagné et remportez {prize} {coin}.",
    "Sie haben gewonnen und erhalten {prize} {coin}."],
  "looser number" : [
    "You did not win.",
    "Vous n'avez pas gagné.",
    "Sie haben nicht gewonnen."],
  "no winner" : [
    "No one won in this round.",
    "Personne n'a gagné à cette manche.",
    "Niemand hat in dieser Runde gewonnen."],
  "flouze invested" : [
    "You have put {amount} {coin} in the common pot.",
    "Vous avez versé {amount} {coin} dans le pot commun.",
    "Sie haben {amount} {coin} in den gemeinsamen Spendentopf eingezahlt."],
  "return on investment" : [
    "You have received {prize} {coin}.",
    "Vous avez reçu {prize} {coin}.",
    "Sie haben {prize} {coin} erhalten."],
  "made the most money" : [
    "You received {prize} {coin}. You also received {stars} {star} because you won the most money during this game.",
    "Vous avez reçu {prize} {coin}.<br>En plus vous recevez {stars} {star} car vous avez gagné le plus d'argent durant ce jeu.",
    "Sie haben {prize} {coin} erhalten.<br> Zusätzlich erhalten Sie {stars} {star}, da Sie während dieses Spiels das meiste Geld gewonnen haben."],
  "chosen star" : [
    "You have chosen the prize : {star}.",
    "Vous avez choisi le lot : {star}.",
    "Sie haben das Los {star} gewählt."],
  "chosen prize" : [
    "You have chosen the prize : {prize} {coin}.",
    "Vous avez choisi le lot : {prize} {coin}.",
    "Sie haben das Los {prize} {coin} gewählt."],
  "won star" : [
    "You have won the prize : {star} !",
    "Vous avez remporté le lot : {star} !",
    "Sie haben das Los {star} gewonnen !"],
  "won prize" : [
    "You have won the prize : {prize} {coin} !",
    "Vous avez remporté le lot : {prize} {coin} !",
    "Sie haben das Los {prize} {coin} gewonnen !"],
  "prize not won" : [
    "You did not win your prize.",
    "Vous n'avez pas remporté votre lot.",
    "Sie haben Ihr Los nicht gewonnen."],
  "starmaster announcement" : [
    "{name} has the most stars and is thus in possession of the sum of {jackpot} {coin} for the 5th game.",
    "{name} a le plus d'étoiles et est ainsi en possesion de la somme de {jackpot} {coin} pour le 5ème jeu.",
    "{name} hat die meisten Sterne und ist damit im Besitz von {jackpot} {coin} für das fünfte Spiel."],
  "you are the starmaster" : [
    "You have the most stars and are thus in possession of the sum of {jackpot} {coin} for the 5th game.",
    "Vous avez le plus d'étoiles et êtes ainsi en possesion de la somme de {jackpot} {coin} pour le 5ème jeu.",
    "Sie haben die meisten Sterne und sind damit im Besitz von {jackpot} {coin} für das fünfte Spiel."],
  "tie" : [
    "Due to the tie in stars, no one wins the jackpot and the fifth game is cancelled.",
    "Dû à l'égalité d'étoiles, personne ne remporte le gros lot et le cinquième jeu est annulé.",
    "Aufgrund der gleichen Anzahl an Sternen gewinnt niemand den Hauptpreis und das fünfte Spiel wird abgebrochen."],
  "wrong awnser" : [
    "Wrong ! The correct awnser to the question '{question}' was : {correct_answer}.",
    "Perdu ! La bonne réponse à la question '{question}' était : {correct_answer}.",
    "Falsch ! Die richtige Antwort auf die Frage '{question}' war : {correct_answer}."],
  "right awnser" : [
    "Congratulations ! Yoou win {prize} {coin} !",
    "Félicitation ! Vous remportez {prize} {coin} !",
    "Herzlichen Glückwunsch ! Sie erhalten {prize} {coin} !"],
  "wait" : [
    "Please wait for the offer from {name}...",
    "Veuillez attendre l'offre de {name} ...",
    "Bitte warten Sie auf das Angebot von {name} ..."],
  "offer" : [
    "{name} offers you {amount} {coin}.",
    "{name} vous fait une offre de {amount} {coin}.",
    "{name} Bietet ihnen {amount} {coin} an"],
  "your offer is accepted" : [
    "Your offer was accepted by the majority.",
    "Votre offre a été acceptée par la majorité.",
    "Ihr Angebot wurde von der Mehrheit angenommen."],
  "offer accepted" : [
    "The offer was accepted by the majority."
    "La proposition à été acceptée par la majorité des joueurs.",
    "Das Angebot wurde von der Mehrheit der Spieler angenommen."],
  "offer received" : [
    "<br>You have received {offer} {coin} from {name}.",
    "<br>Vous avez reçu {offer} {coin} de la part de {name}.",
    "<br>Sie haben {offer} {coin} von {name} erhalten."],
  "lost flouze" : [
    "<br>You have been shaken down {loss} {coin} by {name}"
    "<br>Vous vous êtes fait racketter {loss} {coin} par {name}.",
    "<br>Sie wurden von {name} um {loss} {coin} erpresst."],
  "your last offer is declined" : [
    "Your last offer was not accepted by the majority. The {jackpot} {coin} are therefore withdrawn.",
    "Votre dernière offre n'a pas été acceptée par la majorité. Les {jackpot} {coin} vous sont donc retirés.",
    "Ihr letzter Angebot wurde von der Mehrheit nicht angenommen. Die {jackpot} {coin} werden Ihnen daher entzogen."],
  "last offer declined" : [
    "No agreement was found after these 3 trials so {name} does not win the {jackpot} {coin}.",
    "Aucun accord n'a été trouvé après ces 3 essais donc {name} ne remporte pas les {jackpot} {coin}.",
    "Nach diesen drei Versuchen wurde keine Einigung erzielt, sodass {name} die {jackpot} {coin} nicht gewinnt."],
  "your offer is declined" : [
    "Your offer was not accepted by the majority.",
    "Votre offre n'a pas été acceptée par la majorité.",
    "Ihr Angebot wurde von der Mehrheit nicht angenommen."],
  "offer declined" : [
    "The offer has been refused by at least {players} players.<br>Waiting for a new proposal...",
    "L'offre à été refusée par au moins {players} joueurs.<br>En attente d'une nouvelle proposition...",
    "Das Angebot wurde von mindestens {players} Spielern abgelehnt.<br>Bitte warten sie auf ein neues Angebot..."],
  "final earnings" : [
    "<br>You leave with {flouze} {coin}.",
    "<br>Vous repartez donc avec {flouze} {coin}.",
    "<br>Ihr Endvermögen beträgt {flouze} {coin}."]
}

html_txt = {
  "login" : [
    "Login",
    "Connexion",
    "Anmeldung"],
  "who are you ?" :[
    "Who are you ?",
    "Qui est-tu ?",
    "Wer bist du ?"],
  "name" : [
    "Name",
    "Prénom",
    "Vornahme"],
  "password" : [
    "Password",
    "Mot de passe",
    "Passwort"],
  "log in" : [
    "Log in",
    "Se connecter",
    "Sich anmelden"],
  "game 1" : [
    "Flouze - Game 1",
    "Flouze - Jeu 1",
    "Flouze - Spiel 1"],
  "game 2" : [
    "Flouze - Game 2",
    "Flouze - Jeu 2",
    "Flouze - Spiel 2"],
  "game 3" : [
    "Flouze - Game 3",
    "Flouze - Jeu 3",
    "Flouze - Spiel 3"],
  "game 4" : [
    "Flouze - Game 4",
    "Flouze - Jeu 4",
    "Flouze - Spiel 4"],
  "game 5" : [
    "Flouze - Game 5",
    "Flouze - Jeu 5",
    "Flouze - Spiel 5"],
  "end" : [
    "Flouze - END",
    "Flouze - FIN",
    "Flouze - ENDE"],
  "quiz" : [
    "QUIZ",
    "QUIZ",
    "QUIZ"],
  "donate" : [
    "Donate",
    "Faire un don",
    "Spenden"],
  "share" : [
    "Share",
    "Partager",
    "Teilen"],
  "to share" : [
    "to share",
    "à partager",
    "zum teilen"],
  "possible rejection" : [
    "Your claim may be rejected by the players.",
    "Votre demande peut être refusée par les joueurs.",
    "Ihre Forderung kann von den Spielern abgelehnt werden."],
  "welcome" : [
    "Welcome",
    "Bienvenue",
    "Willkommen"],
  "colors" : [
    "Colors",
    "Couleurs",
    "Farben"],
  "donate star" : [
    "Would you like to give stars ?",
    "Souhaitez-vous donner des étoiles ?",
    "Möchten Sie Sterne vergeben ?"],
  "yes" : [
    "YES",
    "OUI",
    "JA"],
  "no" : [
    "NO",
    "NON",
    "NEIN"],
  "star recipient" : [
    "To whom do you wish to give stars ?",
    "À qui souhaitez-vous donner des étoiles ?",
    "Wem möchten Sie Sterne geben ?"],
  "send" : [
    "Send",
    "Envoyer",
    "Senden"],
  "amount" : [
    "Amount",
    "Montant",
    "Betrag"],
  "quantity" : [
    "Amount",
    "Quantitée",
    "Anzahl"],
  "your awnser" : [
    "Your awnser",
    "Votre réponse",
    "Ihre Antwort"],
  "claim" : [
    "Claim",
    "Réclamer",
    "Einfordern"],
  "back" : [
    "Back",
    "Retour",
    "Zurück"],
  "actually no" : [
    "actually ... no",
    "en fait non",
    "doch nicht"],
  "confirm" : [
    "Confirm",
    "Valider",
    "Bestätigen"],
  "waiting" : [
    "Waiting for the other players...",
    "En attente des autres joueurs...",
    "In Erwartung der anderen Spieler ..."],
  "recipient" : [
    "Recipient",
    "Destinataire",
    "Empfänger"],
  "how many tickets" : [
    "How many tickets do you want to put into play ?",
    "Combien de tickets voulez-vous mettre en jeu ?",
    "Wie viele Tickets möchten Sie einsetzen ?"],
  "tickets amount" : [
    "Amount of tickets",
    "Nombre de tickets",
    "Anzahl Tickets"],
  "no ticket" : [
    "No ticket",
    "Aucun ticket",
    "Kein ticket"],
  "1 ticket" : [
    "1 ticket",
    "1 ticket",
    "1 Ticket"],
  "tickets" : [
    "tickets",
    "tickets",
    "Tickets"],
  "choose a number" : [
    "Choose a number :",
    "Choisissez un nombre :",
    "Wählen sie eine Zahl :"],
  "invest" : [
    "How much would you like to invest ?",
    "Combien souhaitez-vous investir ?",
    "Wie viel möchten Sie investieren ?"],
  "choose prize" : [
    "Choose a prize :",
    "Choisissez un lot :",
    "Wählen sie einen Los :"],
  "please make an offer" : [
    "Please make an offer to the other players :",
    "Veuillez faire une offre aux autres joueurs :",
    "Bitte machen sie den anderen Spielern ein Angebot :"],
  "make offer" : [
    "Make an offer",
    "Faire une proposition",
    "Angebot machen"],
  "remaining money 1" : [
    "You will have",
    "Il vous restera",
    "Sie haben dann noch"],
  "remaining money 2" : [
    "left",
    "",
    "übrig"],
  "declined" : [
    "Declined",
    "Refusé",
    "Abgelehnt"],
  "accepted" : [
    "Accepted",
    "Accepté",
    "Angenommen"],
  "decline" : [
    "Decline",
    "Refuser",
    "Ablehnen"],
  "accept" : [
    "Accept",
    "Accepter",
    "Annehmen"],
  "new offer" : [
    "Make a new offer",
    "Faire une nouvelle proposition",
    "Ein neues Angebot machen"]
}