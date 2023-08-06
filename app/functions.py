from __future__ import with_statement
import calendar
import glob
import json
import logging
import re
import sys
import unicodedata
from os import listdir, path
from urllib.parse import urljoin, urlparse
from flask import request
import gettext
from datetime import datetime
from dateutil import tz
from pathlib import Path


#########################################
# SLUGIFY                               #
#########################################  
def slugify(value:str, allow_unicode:bool=False) ->str:
    """
    The `slugify` function takes a string value and converts it into a slug format by removing special
    characters, converting to lowercase, and replacing spaces with hyphens.
    
    @param value The value parameter is a string that you want to convert into a slug. A slug is a
    URL-friendly version of a string, typically used in URLs or file names.
    @param allow_unicode The `allow_unicode` parameter is a boolean value that determines whether to
    allow Unicode characters in the slug or not. If set to `True`, Unicode characters will be allowed.
    If set to `False`, Unicode characters will be removed from the slug.

    @return Returns a string.
    """

    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


#########################################
# IS SAFE URL                           #
#########################################  
def is_safe_url(target:str) ->str:
    """
    The function `is_safe_url` checks if a target URL is safe by comparing the scheme and netloc of the
    target URL with the current host URL.
    
    @param target The `target` parameter is a string that represents the URL that needs to be checked
    for safety.

    @return Returns a string.
    """

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


#########################################
# GET TRANSLATION                       #
#########################################  
def get_translation(translation:str, localedir:str, lang:str):
    """
    The function `get_translation` installs a translation for a specific language using the `gettext`
    module.
    
    @param translation The name of the translation file or domain. This is typically a string that
    represents the name of the translation file or domain that contains the translated strings.
    @param localedir The `localedir` parameter is the directory where the translation files are located.
    These translation files contain the translated strings for different languages.
    @param lang The `lang` parameter is the language code for the desired translation. It is used to
    specify the language of the translation file to be loaded.
    """
  
    try:
        lang = gettext.translation(translation, localedir=localedir, languages=[lang])
        lang.install()
    except FileNotFoundError as e:
        msg = f"{ __file__} | Line {e.__traceback__.tb_lineno} | {repr(e)}"
        sys.exit(msg)   


#########################################
# CONVERT INTO LOCAL TIME               #
#########################################  
def convert_into_local_time(to_zone:str, utc:datetime) ->list:
    """
    The function `convert_into_local_time` takes a time zone and a UTC datetime as input and returns
    the corresponding local time in that time zone.
    
    @param to_zone The `to_zone` parameter is a string that represents the desired time zone to
    convert the UTC time to. It should be in the format of a valid time zone identifier, such as
    "America/New_York" or "Asia/Tokyo".
    @param utc The `utc` parameter is a `datetime` object representing a specific point in time in
    Coordinated Universal Time (UTC).
    
    @return The function `convert_into_local_time` returns a list with two elements. The first
    element is a boolean value indicating whether the conversion was successful or not. The second
    element is the local time in the specified time zone if the conversion was successful, or an
    error message if an exception occurred.
    """

    try:
        from_zone = tz.gettz("UTC")
        to_zone = tz.gettz(to_zone)
    
        utc = datetime.utcnow()
        utc = utc.replace(tzinfo=from_zone)

        local = utc.astimezone(to_zone)

        return [True, local]
    except Exception as e:
        result = [False, repr(e)]


#########################################
# GET MODELS                            #
#########################################  
def get_models(models_path:str, is_authenticated:bool, run_date:str) ->list:
    """
    The function `get_models` retrieves a list of models from a specified path, filtering them based on
    authentication status and a given run date.
    
    @param models_path The `models_path` parameter is a string that represents the path to the directory
    where the models are stored. This directory should contain subdirectories for each run date, and
    each subdirectory should contain JSON files representing the models.
    @param is_authenticated A boolean value indicating whether the user is authenticated or not.
    @param run_date The `run_date` parameter is a string representing the date in the format "YYYYMMDD".
    It is used to construct the full path to the models directory by appending it to the `models_path`.

    @return The function `get_models` returns a list. The first element of the list is a boolean value
    indicating whether the function executed successfully or not. The second element is a nested list
    containing the result data. The nested list contains two elements:
    """

    try:
        full_models_path = path.join(models_path, run_date)

        month_name = calendar.month_name[ int(run_date[4:6]) ].title()
        string_date = f"{run_date[6:8]} {month_name} {run_date[0:4]}"

        data = []

        dir_list = glob.glob(full_models_path + "*/webp")
        for dir in sorted(dir_list):
    
            models = []

            json_files = [filename for filename in listdir(dir) if filename.endswith('.json')]
            for json_file in sorted(json_files):

                if path.exists( path.join(dir, json_file) ):
                    with open( path.join(dir, json_file) ) as j:
                            
                        jdata = json.load(j)

                        if is_authenticated or jdata["pubblico"]:
                   
                            model = {}

                            if json_file.startswith("map_"):
                                title = jdata["etichetta"].split("_")[1:]

                            if json_file.startswith("section_"):   
                                title = jdata["etichetta"].split("_")

                            title = [dir.title() for dir in title]
                            model["title"] = ' '.join(title)

                            if json_file.startswith("map_"):
                                thumb_filepath = path.join(dir, "thumbs", "thumb_" + jdata["immagini"][0]["like"])
              
                            if json_file.startswith("section_"):
                                thumb_filename = Path(jdata["immagini"][0]["file"]).with_suffix('')
                                thumb_filepath = path.join(dir, "thumbs", "thumb_" + str(thumb_filename))
                   
                            thumbs = glob.glob( thumb_filepath + "*.webp" )
                            model["thumbs"] = path.basename(thumbs[0]) if thumbs else ""

                            model["dataEmissione"] = jdata["dataEmissione"]
                            model["etichetta"] = jdata["etichetta"]
                            model["percorso"] = jdata["percorso"]
                            model["tags"] = [jdata["nomeModello"], jdata["tipo"]]

                            models.append(model)
    
            data.append(models)
        result = [True, [[string_date], data]]
    except Exception as e:
        logging.error(repr(e))
        result = [False, repr(e)]

    return result  


#########################################
# GET VARIABLES                         #
#########################################  
def get_variables(models_path:str, is_authenticated:bool, name:str) ->list:
    """
    The function `get_variables` takes in a `models_path` (a string representing the path to a
    directory), a `name` (a string representing a name), and an `is_authenticated` (a boolean
    representing whether the user is authenticated) and returns a list of variables.
    
    @param models_path The `models_path` parameter is a string that represents the path to the directory
    where the models are stored.
    @param name The `name` parameter is a string that represents the name of a model.
    @param is_authenticated A boolean value indicating whether the user is authenticated or not.

    @return Returns a list containing two elements. The first element is a
    boolean value indicating the success or failure of the function, and the second element is a list of
    variables.
    """

    try:
        variables = []

        jfile = path.join(models_path, "webp", name + ".json")

        if path.exists( jfile ):
            with open(jfile) as j:
                data = json.load(j)

                string_date = f'{data["percorso"][6:8]} {calendar.month_name[ int( data["percorso"][4:6] ) ].title()} {data["percorso"][0:4]}'
                string_run = f'Corsa del {data["percorso"][8:10]} UTC'

                images = data["immagini"] 

                if is_authenticated or data["pubblico"]:
                    for img in images:

                        variable = {}

                        if name.startswith("map_"):
                            variable["title"] = img["title"]

                            thumbs = glob.glob( path.join(models_path, "webp", "thumbs", "thumb_" + img["like"] + "*.webp") )
                
                        if name.startswith("section_"):
                            variable["title"] = img["name"]
                    
                            thumb_filename = Path(img["file"]).with_suffix('')
                            thumb_filepath = path.join(models_path, "webp", "thumbs", "thumb_" + str(thumb_filename))
                            thumbs = glob.glob( thumb_filepath + "*.webp" )
                         
                        variable["thumbs"] = path.basename(thumbs[0]) if thumbs else ""
                    
                        variable["tags"] = [data["nomeModello"], data["tipo"]]
                        variable["dataEmissione"] = data["dataEmissione"]
                        variable["etichetta"] = data["etichetta"]

                        if name.startswith("map_"):
                            variable["variable"] = img["like"]

                        if name.startswith("section_"):
                            variable["variable"] = img["file"]

                        variable["percorso"] = data["percorso"]

                        variables.append(variable)

        result = [True, [[string_date, string_run], variables]]
    except Exception as e:
        logging.error(repr(e))
        result = [False, repr(e)]

    return result  


def get_variable_images(models_path:str, is_authenticated:bool, name:str, variable:str) ->list:
    """
    The function `get_variable_images` retrieves a list of images based on a given variable name from a
    JSON file, along with additional information such as the date and run details, and returns the
    result as a list.
    
    @param models_path The `models_path` parameter is a string that represents the path to the directory
    where the models are stored.
    @param is_authenticated A boolean value indicating whether the user is authenticated or not.
    @param name The `name` parameter is a string that represents the name of the model.
    @param variable The `variable` parameter is a string that represents a specific variable. It is used
    to filter the images based on this variable.

    @return The function `get_variable_images` returns a list. The first element of the list indicates
    whether the operation was successful or not. If the operation was successful, the second element of
    the list contains a nested list. The nested list contains three elements: `string_date`,
    `string_run`, and `string_variable`. The fourth element of the nested list is a list of file names.
    """

    try:
        jfile = path.join(models_path, "webp", name + ".json")

        if path.exists( jfile ):
            with open(jfile) as j:
                data = json.load(j)

                if name.startswith("section_"):
                    images = data["immagini"]
                    for e in images:
                        for i,v in e.items():
                            if v == variable:
                                string_variable = e["name"]
    
                    string_date = f'{data["percorso"][6:8]} {calendar.month_name[ int( data["percorso"][4:6] ) ].title()} {data["percorso"][0:4]}'
                    string_run = f'Corsa del {data["percorso"][8:10]} UTC'

                    if is_authenticated or data["pubblico"]:   
                        v= Path(variable).with_suffix('')
                        list_of_files = [path.basename(x) for x in glob.glob( path.join(models_path, "webp", str(v) + "*.webp") )]
                    
                if name.startswith("map_"):
                        images = data["immagini"]
                        for e in images:
                            for i,v in e.items():
                                if v == variable:
                                    string_variable = e["title"]
        
                        string_date = f'{data["percorso"][6:8]} {calendar.month_name[ int( data["percorso"][4:6] ) ].title()} {data["percorso"][0:4]}'
                        string_run = f'Corsa del {data["percorso"][8:10]} UTC'

                        if is_authenticated or data["pubblico"]:   
                            list_of_files = [path.basename(x) for x in glob.glob( path.join(models_path, "webp", variable + "*.webp") )]

                result = [True,[[string_date, string_run, string_variable], list_of_files]]
    except Exception as e:
        logging.error(repr(e))
        result = [False, repr(e)]

    return result  