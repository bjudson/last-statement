# coding: utf-8

import os
import time
from datetime import datetime

from passlib.hash import bcrypt

from flask import (Blueprint, request, render_template, url_for, flash,
                   redirect)
from flask.ext.login import (LoginManager, login_required, login_user,
                             logout_user, current_user)

from last.app import app
from models import db, User
from last.forms import LoginForm

os.environ['TZ'] = 'America/Chicago'
time.tzset()

admin = Blueprint('admin', __name__,
                  template_folder='templates',
                  static_folder='static')

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    return db.session.query(User).get(userid)


@app.route('/login', methods=['GET', 'POST', 'OPTIONS'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and bcrypt.verify(form.password.data,
                                              user.password):
            if login_user(user):
                user.last_login = datetime.now()
                db.session.commit()

                flash('Logged in %s' % user.email, 'success')
                return redirect(request.args.get('next') or
                                url_for('admin.index'))
            else:
                flash('This user is disabled', 'error')
        else:
            flash('Wrong email or password', 'error')

    return render_template('login.html', form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out', 'success')
    return redirect(url_for('index'))


@admin.route('/', methods=['GET', 'OPTIONS'])
@login_required
def index():
    return render_template('admin/admin.html', user=current_user.email)
