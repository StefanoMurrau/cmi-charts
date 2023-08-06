import bcrypt
import click
from flask.cli import with_appcontext
from app.database import db
from app.models import Users


#########################################
# ADD USER                              #
#########################################
@click.command("add-user")
@click.option("--mail", "-m", required=True)
@click.option('--password', "-p", required=True)
@with_appcontext
def add_user(mail:str, password:str) ->str:
    """
    The `add_user` function takes in a user's email and password, hashes the password using bcrypt, and
    adds the user to the database.
    
    @param mail The `mail` parameter is a string that represents the email address of the user being
    added.
    @param password The `password` parameter is a required option that represents the password for the
    user. It is a string that will be encoded using UTF-8 before being hashed using the bcrypt
    algorithm.
    
    @return The function `add_user` returns a string. If the user is successfully created, it returns a
    success message indicating that the user has been created. If there is an exception during the
    creation of the user, it returns an error message indicating the reason for the failure.
    """
    
    bytePwd = password.encode('utf-8')
    mySalt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytePwd, mySalt)

    try:
        user = Users(mail=mail, password=hash)
        db.session.add(user)
        db.session.commit()
        print( f"Utente {mail} creato con successo" )
    except Exception as e:
        print( f"Impossibile creare l'utente {mail}: {format(e)}" )
    
    