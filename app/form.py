from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class login_form(FlaskForm):
    mail = EmailField("Mail", validators=[DataRequired()], id="mail", name="mail", render_kw={"placeholder": "Utente", "class":"form-control"})
    password = PasswordField("Password", validators=[DataRequired()],  id="password", name="password", render_kw={"placeholder": "Password", "class":"form-control"})
    submit = SubmitField("Autenticati", render_kw={"class":"btn btn-primary"})
    