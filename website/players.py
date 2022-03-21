import datetime

class Player(object):
    def __init__(player, ID, name, password, main_color, sec_color, engine):
        player.engine
        player.ID = ID
        player.sid = None
        player.name = name
        player.password = password
        player.flouze = 0
        # Dans le jeu 3 l'argent est mis de coté
        player.saved_flouze = 0
        player.stars = 0
        player.color = main_color
        player.sec_color = sec_color
        player.choix = None
        # Indique si le joueur est en attente
        player.is_done = False
        # Quantitée a partager dans 'partager.htlm'
        player.last_profit = 0
        player.messages = []
        return player
    
    def send_message(player, message):
        socketio = player.engine.socketio
        player.messages.append((datetime.datetime.now(), message))
        socketio.emit('message', message, room=player.sid)
    
    def send_money(player, receiver, amount):
        assert(player.flouze >= amount)

        player.flouze -= amount
        receiver.flouze += amount

        player.game.log(f"{player.name} a fait un don de {amount} Pièces à "\
                        f"{receiver.name}.")
    
        updates = [("flouze", receiver.flouze)]
        player.game.update_fields(updates, [receiver])
        
        message = f'Vous avez envoyé {amount} '\
                   '<img src="/static/images/coin.png" style="width:22px" '\
                  f'alt="Coin"> &nbsp; à {receiver.name}.'
        flash(Markup(message, category='success'))
        
        message = f'Vous avez reçu {amount} <img src="/static/images/coin.png"'\
                   ' style="width:22px" alt="Coin"> &nbsp;  de la part de '\
                  f'{player["name"]}.'
        receiver.send_message(message)

        player.game.save_data()
        
    
    def send_star(player, receiver, sent_stars):
        assert(player.stars >= sent_stars)

        player.stars -= sent_stars
        receiver.stars += sent_stars

        player.game.log(f"{player.name} a légué {sent_stars} "\
                        f"étoile{'s' if sent_stars > 1 else ''} "\
                        f"à {receiver.name}.")
        
        updates = [(f"player{player.ID}_star", f" {player.stars}"),
                   (f"player{receiver.ID}_star", f" {receiver.stars}")] 
        player.game.update_fields(updates)
        
        message = f'Vous avez envoyé {sent_stars} <i class="fa fa-star"></i> '\
                  f'à {receiver.name}.'
        flash(Markup(message, category='success'))
        
        message = f'Vous avez reçu {sent_stars} <i class="fa fa-star"></i> '\
                  f'de la part de {player.name}.'
        receiver.send_message(message)

        player.game.save_data()


    def share_profit(player, amounts):
        assert(player.last_profit)
        assert(sum(amounts) <= player.last_profit)
        assert(sum(amounts) <= player.flouze)
        for receiver, amount in zip(player.other_players, amounts):
            if amount:
                player.send_money(receiver, amount)
        player.last_profit = None
    
