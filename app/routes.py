from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User, MessageLog
from .forms import RegistrationForm, LoginForm, EncodeForm, DecodeForm
from .encoder import encode_message
from .decoder import decode_snippets

auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username taken.')
        else:
            u = User(username=form.username.data, role=form.role.data)
            u.set_password(form.password.data)
            db.session.add(u); db.session.commit()
            flash('Registered! Please log in.')
            return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u and u.check_password(form.password.data):
            login_user(u)
            return redirect(url_for('main.sender' if u.role=='sender' else 'main.receiver'))
        flash('Invalid creds.')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@main_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@main_bp.route('/sender', methods=['GET','POST'])
@login_required
def sender():
    if current_user.role != 'sender':
        return redirect(url_for('main.receiver'))
    form = EncodeForm()
    snippets = []
    if form.validate_on_submit():
        snippets = encode_message(form.secret.data)
        log = MessageLog(user_id=current_user.id, direction='encode',
                         input_text=form.secret.data,
                         output_text='\n'.join(snippets))
        db.session.add(log); db.session.commit()
    return render_template('sender.html', form=form, snippets=snippets)

@main_bp.route('/receiver', methods=['GET','POST'])
@login_required
def receiver():
    if current_user.role != 'receiver':
        return redirect(url_for('main.sender'))
    form = DecodeForm()
    message = ''
    if form.validate_on_submit():
        snippets = [line.strip() for line in form.snippets.data.splitlines() if line.strip()]
        message = decode_snippets(snippets)
        log = MessageLog(user_id=current_user.id, direction='decode',
                         input_text=form.snippets.data,
                         output_text=message)
        db.session.add(log); db.session.commit()
    return render_template('receiver.html', form=form, message=message)
