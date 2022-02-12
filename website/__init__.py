from flask import Flask
from .models import Player

pages = ["Jeu1-choix.html", "Jeu2-choix.html", "Jeu3-choix.html", "Jeu4-choix.html", "Jeu5-choix.html"]
iterator = 3

players = []
file = open("players.txt", "r")
for p in range(5):
    line = file.readline().split()
    players.append(Player(p, line[0], line[1]))
file.close()

from .globals import initialize
globals.initialize()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app
