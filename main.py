from website import create_app

pages=["Jeu1-choix.html","Jeu2-choix.html","Jeu3-choix.html","Jeu4-choix.html","Jeu5-choix.html"]
iterator=0

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
