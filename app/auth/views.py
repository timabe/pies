from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User, Pies, Orders
from .forms import LoginForm, RegistrationForm, PieChoices

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('auth.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    name=form.name.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/', methods = ['GET','POST'])
@login_required
def index():
    pies = Pies.query.order_by(Pies.name.desc()).all()
    form = PieChoices()
    form.pie_id.choices =[(p.id, p.name) for p in Pies.query.order_by('name')]
    if form.validate_on_submit():
        pie_id = form.pie_id.data
        order = Orders(pie_id=pie_id,user_id=current_user._get_current_object().id)
        db.session.add(order)
        pie = Pies.query.filter_by(id=pie_id).first()
        return render_template('auth/order.html', pie = pie)
    return render_template('auth/index.html', form = form)

@auth.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    orders = Orders.query.filter_by(user_id=user.id).count()
    return render_template('auth/user.html', user=user, orders = orders)

@auth.route('/order/<id>')
@login_required
def order(id):
    pie = Pies.query.filter_by(id=id).first_or_404()
    pie_name = pie.name
    user_name = current_user._get_current_object().username
    form = OrderForm(pie=pie_name,name=user_name)
    return render_template('auth/order.html', pie=pie, form=form)

