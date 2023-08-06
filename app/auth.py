import datetime
import bcrypt
from flask import (Blueprint, abort, current_app, flash, redirect, request,
                   session, url_for)
from flask_login import login_required, login_user, logout_user
from jinja2 import TemplateNotFound
from app.database import db
from app.form import login_form
from app.models import User_actions, Users


auth = Blueprint('auth', __name__)


@auth.route('/autenticazione', methods = ['POST'])
def login_post():
    """
    This function handles the login process by validating the user's credentials, logging them in, and
    recording the login action in the database.
    
    @return The code is returning a redirect to the 'main.index' route.
    """

    try:
        form = login_form()

        if form.validate_on_submit():

            mail = form.mail.data.lower().strip()
            password = form.password.data.strip()
        
            user = Users.query.filter_by(mail=mail).first()

            if not user or not bcrypt.checkpw(password.encode('utf8'), user.password):
                flash('Credenziali errate.', 'danger')
            else:
                login_user(user)
                session['user'] = user.id
                session["last_active"] = datetime.datetime.now()
            
                user_action = User_actions(user_id=user.id, remote_addr=request.remote_addr, http_user_agent=request.headers.get('User-Agent'), action_id=1)
                db.session.add(user_action)
                db.session.commit()

                flash('Autenticazione riuscita.', 'success')

        return redirect(url_for('main.index'))
    except TemplateNotFound:
        abort(404)


@auth.route("/disconnessione")
@login_required
def logout():
    """
    The above function logs out the user, records the user action in the database, and redirects the
    user to the main index page.
    
    @return a redirect to the 'main.index' route.
    """

    try:
        user = session['user']
        user_action = User_actions(user_id=user, remote_addr=request.remote_addr, http_user_agent=request.headers.get('User-Agent'), action_id=2)
        db.session.add(user_action)
        db.session.commit()

        logout_user()
        return redirect(url_for('main.index'))
    except TemplateNotFound:
        abort(404)
