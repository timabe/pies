from flask import render_template, redirect, abort, request, flash, url_for
from flask_login import login_required, current_user
from .. import db
from . import main
from ..models import User, Pies, Orders

@main.route('/', methods = ['GET','POST'])
def index():
    pies = Pies.query.order_by(Pies.name.desc()).all()
    return render_template('index.html', pies = pies)

