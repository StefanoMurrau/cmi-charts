import locale
import logging.config
import os
import sys
from os import path
from typing import Union
from flask import Flask, current_app, render_template
from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_seeder import FlaskSeeder
from app.database import db
from app.form import login_form
from flask_session import Session
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import NotFound


locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')


sess = Session()
login_manager = LoginManager()
migrate = Migrate()
seeder = FlaskSeeder()
scheduler = APScheduler()


def create_app() ->Flask:
    """
    Create and configure the app
    
    @return The app object.
    """

    app = Flask(__name__, instance_relative_config=True)

    if not os.path.isdir(app.instance_path):
        os.makedirs(app.instance_path)


    with app.app_context():
        try:
            app.config.from_object("config.DevelopmentConfig")
            logging.config.dictConfig( app.config["LOGGING_CONFIG"] )
        except Exception as e:
            msg = f"{ __file__} | Line {e.__traceback__.tb_lineno} | {repr(e)} | Cannot load config file."
            sys.exit(msg)

        if not app.config.get("APPLICATION_ROOT") == "/":
            app.wsgi_app = DispatcherMiddleware(
                NotFound(),{
                    app.config.get("APPLICATION_ROOT") : app.wsgi_app
                }
            )


        #We need to import all the models to permit the automigrate of the tables with Alembic
        #Add all custom commands
        from app.commands import add_user
        from app.models import Actions, User_actions, Users
        
        app.cli.add_command(add_user)
   

        db.init_app(app)
        migrate.init_app(app, db)
        sess.init_app(app)
        seeder.init_app(app, db)
        scheduler.init_app(app)
      
        from . import scheduled_tasks
        scheduler.start()
           
      
        SCHEMA = app.config.get("PROJECT_NAME")
        try:
            # Ensure FOREIGN KEY for sqlite3
            if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
                def _fk_pragma_on_connect(dbapi_con, con_record):
                    dbapi_con.execute('pragma foreign_keys=ON')
                    dbapi_con.execute("ATTACH '" + os.path.join( os.path.abspath(os.path.dirname(__file__)), "..", "instance", SCHEMA + ".db") + "' AS '" + SCHEMA + "'")
               
                from sqlalchemy import event
                event.listen(db.engine, 'connect', _fk_pragma_on_connect)
        except Exception as e:
            msg = f"{ __file__} | Line {e.__traceback__.tb_lineno} | {repr(e)} | Failed to manage database."
            logging.error(msg)
            sys.exit(msg)
            

        login_manager.init_app(app)
        login_manager.login_view = "auth.login"
        login_manager.login_message = ''


        @login_manager.user_loader
        def load_user(user_id:str) -> Union[str, None]:
            return Users.query.get(user_id)
        

        #########################################
        # 404 PAGE                              #
        #########################################
        def page_not_found(e):
            """
            The function `page_not_found` is a handler for the 404 error and renders a template for a page not
            found error with some additional context variables.
            
            @param e The parameter "e" in the "page_not_found" function is used to capture any exception or
            error that occurred when the 404 error was raised. It allows you to access information about the
            error, such as the error message or traceback, if needed.

            @return The function `page_not_found` is returning a rendered template for a 404 error page. The
            template is passed the following variables: `form`, `display_name`, `base_href`, and `title`. The
            function also returns a status code of 404.
            """
    
            return render_template(
                '404.html', 
                form=login_form(), 
                base_href = current_app.config["APPLICATION_ROOT"],
                display_name=current_app.config["DISPLAY_NAME"],
                title = "Pagina non trovata"), 404
                            
        app.register_error_handler(404, page_not_found)

        #########################################
        # 403 PAGE                              #
        #########################################
        def forbidden(e):
            """
            The function `forbidden` is a handler for the 403 error, which renders a template for access denied
            and returns a 403 status code.
            
            @param e The parameter "e" in the "forbidden" function is typically used to capture any exception or
            error that occurred. In this case, it is not being used in the function body, so it can be safely
            ignored.

            @return The function `forbidden` is returning a tuple containing two values: a rendered template and
            the HTTP status code 403.
            """

            return render_template(
                '403.html', 
                form=login_form(),
                base_href = current_app.config["APPLICATION_ROOT"],
                display_name=current_app.config["DISPLAY_NAME"],
                title = "Accesso negato"), 403

        app.register_error_handler(403, forbidden)
            
        #########################################
        # 500 PAGE                              #
        #########################################
        def internal_server_error(e):
            """
            The function `internal_server_error` is a handler for the 500 Internal Server Error, which renders a
            template with login form, display name, base href, and title.
            
            @param e The parameter "e" in the function "internal_server_error" is used to capture the exception
            object that caused the internal server error. This allows you to access information about the error,
            such as the error message or stack trace, and handle it accordingly.
            
            @return The function `internal_server_error` is returning a rendered template with the following
            arguments:
            """

            return render_template(
                '500.html', 
                form=login_form(), 
                base_href = current_app.config["APPLICATION_ROOT"],
                display_name=current_app.config["DISPLAY_NAME"], 
                title = "Errore interno al server"), 500

        app.register_error_handler(500, internal_server_error)


        #Blueprints
        with app.app_context():
            from app.auth import auth
            from app.main import main

            app.register_blueprint(auth)
            app.register_blueprint(main)
           
      
    return app
