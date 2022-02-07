from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from __main__ import pages, iterator
import json
import random
from .models import User

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    players = User.query.all()
    if current_user.first_name == "felix":
        # if request.method == 'POST':
        #     if request.form['boutton'] == 'increment':
        #         iterator=1
        return render_template("monitoring.html" , players=players, pages=pages, iterator=iterator)
    players = User.query.filter(User.first_name!=current_user.first_name)
    if request.method == 'POST':
        if request.form['boutton'] == 'increment':
            current_user.flouze=random.randint(0,100000)
            current_user.stars+=1
            db.session.commit()
        if request.form['boutton'] == 'don':
            return render_template("faire_un_don.html", user=current_user , players=players)
        if request.form['boutton'] == "jeu1-choix":
            tickets=request.form.get('tickets')
            print(tickets)
            if tickets==None :
                flash('Veuiller faire un choix', category='error')
                return render_template(pages[iterator], user=current_user , players=players)
            flash('Vous avez choisis '+tickets+' tickets', category='success')
    return render_template(pages[iterator], user=current_user , players=players)

    return jsonify({})
