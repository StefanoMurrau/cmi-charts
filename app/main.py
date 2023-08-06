from __future__ import with_statement
import json
from os import path
from flask import Blueprint, abort, current_app, jsonify, render_template, flash, request, redirect, url_for, send_from_directory
from flask_login import current_user
from jinja2 import TemplateNotFound
from app.form import login_form
from app.functions import get_models, get_variables, get_variable_images, convert_into_local_time
import glob
from datetime import datetime
import logging
from markupsafe import escape



BASEDIR = path.abspath( path.dirname(__file__) )


main = Blueprint('main', __name__)


@main.route("/")
def index():
    """
    The index function redirects the user to the dashboard page with the current date as a parameter.
    
    @return The code is returning a redirect to the URL for the 'main.dashboard' route with a parameter
    'day' set to the current date in the format "YYYYMMDD".
    """

    local = convert_into_local_time('Europe/Rome', datetime.utcnow())
    day = local[1].strftime("%Y%m%d")
        
    return redirect( url_for('main.dashboard', day=day) ), 301


@main.route("/<day>/")
def dashboard(day:str):
    """
    The function `dashboard` is a route handler that renders a dashboard template with data retrieved
    from models based on the specified day parameter.
    
    @param day The `day` parameter is a string that represents a specific day in the format "YYYYMMDD".
    It is used to retrieve models and display data on the dashboard for that particular day.

    @return a rendered template called "dashboard.html" with various variables passed to it, including
    display_name, base_href, title, data, form, type, and url.
    """

    try:
        day = escape(day)

        is_authenticated = current_user.is_authenticated
        MODELS_PATH = path.join(BASEDIR, *current_app.config["MODELS_PATH"]) 

        data = get_models(MODELS_PATH, is_authenticated, day)

        if not data[0]:
            flash("Errore nel caricamento dei modelli", "danger")

        return render_template(
            "dashboard.html", 
            display_name=current_app.config["DISPLAY_NAME"],
            base_href = current_app.config["APPLICATION_ROOT"],
            title="Cruscotto", 
            sidebar = "dashboard",
            data=data[1], 
            form = login_form(),
            url="main.variables_overview"
        )
    except TemplateNotFound:
        abort(404) 


@main.route('/<run>/<name>/')
def variables_overview(run:str, name:str):
    """
    The function `variables_overview` is a route in a Flask application that renders a template to
    display an overview of variables for a specific run and name.
    
    @param run The "run" parameter is a string that represents a unique identifier for a specific run or
    model. It is used to locate the model files in the file system.
    @param name The `name` parameter is a string that represents the name of a model. It is used to
    retrieve variables related to that model.

    @return a rendered template called 'variables_overview.html'. The template is being passed several
    variables including 'display_name', 'base_href', 'title', 'data', 'sidebar', 'form', and 'url'.
    """

    try:
        run = escape(run)
        name = escape(name)

        is_authenticated = current_user.is_authenticated
        MODEL_PATH = path.join(BASEDIR, *current_app.config["MODELS_PATH"], run)

        data = get_variables(MODEL_PATH, is_authenticated, name)
        if not data[0]:
            flash("Errore nel caricamento dei modelli", "danger")

        title = name.split("_")
        title = [e.title() for e in title]
        title = ' '.join(title)

        return render_template(
            'variables_overview.html', 
            display_name=current_app.config["DISPLAY_NAME"],
            base_href = current_app.config["APPLICATION_ROOT"],
            title="Panoramica variabili del modello " + title, 
            data=data[1],
            sidebar = "variables_overview",
            form = login_form(), 
            url='main.variable_images'
        )   
    except TemplateNotFound:
        abort(404)

    
@main.route('/<run>/<name>/<variable>/')
def variable_images(run:str, name:str, variable:str):
    """
    The `variable_images` function is a route in a Python Flask application that renders a template to
    display images for a specific variable in a model.
    
    @param run The `run` parameter is a string that represents the run of the model. It is used to
    specify the directory path where the model is located.
    @param name The `name` parameter is a string that represents the name of a model.
    @param variable The `variable` parameter is a string that represents the variable for which you want
    to retrieve images. It is used in the `get_variable_images` function to fetch the images related to
    that variable.
    
    @return a rendered template called 'variable_images.html'. The template is being passed several
    variables including 'display_name', 'base_href', 'title', 'run', 'data', 'sidebar', and 'form'.
    """

    try:

        is_authenticated = current_user.is_authenticated
        MODEL_PATH = path.join(BASEDIR, *current_app.config["MODELS_PATH"], run)

        data = get_variable_images(MODEL_PATH, is_authenticated, name, variable)
        if not data[0]:
            flash("Errore nel caricamento dei modelli", "danger")

        title = name.split("_")[1:]
        title = [e.title() for e in title]
        title = ' '.join(title)

        return render_template(
            'variable_images.html', 
            display_name=current_app.config["DISPLAY_NAME"],
            base_href = current_app.config["APPLICATION_ROOT"],
            title = "Immagini per " + data[1][0][2] + " del modello " + title, 
            run=run,
            data=data[1],
            sidebar = "variable_images",
            form = login_form()
        )   
    except TemplateNotFound:
        abort(404)

 
@main.route('/get-archive-models/', methods = ['POST'])
def get_archive_models():
    """
    The function `get_archive_models` is a route in a Python Flask application that receives a POST
    request, retrieves a JSON payload, and returns a JSON response containing a formatted URL.
    
    @return a JSON response. The response contains a list with two elements. The first element is a
    boolean value indicating whether the operation was successful or not. The second element is a JSON
    object containing the "href" value.
    """

    try:
        base_href = current_app.config["APPLICATION_ROOT"]
        r = request.get_json()
        href = r["formatted_date"] if base_href == "/" else (base_href + "/" + r["formatted_date"])
        result = {"success":True, "value": href}
    except Exception as e:
        jmsg = {"success":False, "value": repr(e)}
        logging.error(jmsg)
        result = jmsg

    return jsonify(result)


@main.route('/get-availables-date/', methods = ['POST'])
def get_availables_date():
    """
    The function `get_availables_date` retrieves a list of available dates from a specified directory
    path and returns it as a JSON response.
    
    @return a JSON object. If there are no exceptions, the JSON object will have the following
    structure:
    {
      "success": true,
      "dirlist": "[list of available dates as a JSON string]"
    }
    """

    try:
        full_models_path = path.join(BASEDIR, *current_app.config["MODELS_PATH"], "*")
        dir_list = glob.glob(full_models_path, recursive=True)

        dir_list = [path.basename(e)[:-2] for e in dir_list]
        dir_list = list(dict.fromkeys(dir_list))

        local = convert_into_local_time('Europe/Rome', datetime.utcnow())
        day = local[1].strftime("%Y%m%d")
        dir_list.append(day)
        
        json_string = json.dumps(dir_list)
        result = {"success":True, "dirlist": json_string}
    except Exception as e:
        jmsg = {"success":False, "value": repr(e)}
        logging.error(jmsg)
        result = jmsg

    return result