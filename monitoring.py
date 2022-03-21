class Monitor(object):
    def __init__(self):
        pass

    def refresh_all_():
        socketio.emit('refresh', None, broadcast=True)

    def save_data():
        global admin_sid
        with open("data.pck", 'wb') as file:
            pickle.dump((gameState, players, log), file)
        if config.admin_sid:
            socketio.emit('refresh', None, room=config.admin_sid)

    def update_fields(changes, players=None):
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
        update_fields([("count", f"{count} / {total}")], players=(p  for p in players if p["done"]))


def is_everyone_done():
    return all(p['done'] for p in players)