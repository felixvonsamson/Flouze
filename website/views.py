from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json
import random
from .models import User

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if request.form['increment'] == 'increment':
            current_user.flouze=random.randint(0,100000)
            current_user.stars+=1
            db.session.commit()

    players = User.query.all()
    return render_template("home.html", user=current_user , players=players)

    return jsonify({})
