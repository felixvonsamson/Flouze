from website import create_app
from flask_socketio import SocketIO

socketio, app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
