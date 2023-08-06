from os import path, remove, listdir, makedirs
from pathlib import Path
from PIL import Image
from glob import glob
from . import scheduler
import logging
from datetime import datetime, timedelta
import pytz
import json
from bs4 import BeautifulSoup as bs4
import shutil


@scheduler.task(
    "interval",
    id="process_models",
    seconds=60,
    max_instances=1
)
def process_models():
    """
    The function `process_models` performs various tasks related to processing models, including
    creating webp images and converting XML sections to JSON.
    """

    try:
        with scheduler.app.app_context():

            def create_webp(dir:str, size:tuple, models_path:str, ext:str="png", delete_origin:bool=False):
                """
                The function `create_webp` takes a directory path, image size, models path, file extension, and a
                flag to delete the original image, and converts all PNG images in the specified directory to WebP
                format, saving them in a new "webp" directory and creating thumbnails in a "thumbs" subdirectory.
                
                @param dir The `dir` parameter is a string that represents the directory where the PNG images are
                located. This directory should be a subdirectory of the `models_path` directory.
                @param size The `size` parameter is a tuple that specifies the desired dimensions of the thumbnail
                image. It should be in the format `(width, height)`.
                @param models_path The `models_path` parameter is the path to the directory where the images are
                located.
                @param ext The `ext` parameter is a string that specifies the file extension of the images to be
                converted to webp format. By default, it is set to "png", but you can change it to any other image
                file format such as "jpg" or "jpeg" if needed.
                @param delete_origin The `delete_origin` parameter is a boolean flag that determines whether or not
                to delete the original image file after converting it to WebP format. If `delete_origin` is set to
                `True`, the original image file will be deleted. If it is set to `False` (default), the
                """

                try:
                    for png in glob( path.join(models_path, dir, "*." + ext) ):
                                
                        destination_dir = path.join(models_path, dir, "webp")
                        destination = path.join(destination_dir, Path(png).stem + ".webp")

                        if not path.exists(destination_dir):
                            makedirs(destination_dir)

                        if not path.exists(destination): 
                            
                            image = Image.open(png)
                            image.save(destination, format="webp")
                                
                        thumb_destination_dir = path.join(models_path, dir, "webp", "thumbs")
                        thumb_destination = path.join(thumb_destination_dir, "thumb_" + Path(png).stem + ".webp")

                        if not path.exists(thumb_destination_dir):
                            makedirs(thumb_destination_dir)

                        if not path.exists(thumb_destination): 
                                    
                            image = Image.open(png)
                            image.thumbnail(size, Image.Resampling.LANCZOS)
                            image.save(thumb_destination, format="webp")

                        if delete_origin:
                            if path.exists(destination) and path.exists(thumb_destination):
                                remove(png) 
                except Exception as e:
                    msg = f"{ __file__} | Line {e.__traceback__.tb_lineno} | {repr(e)}"
                    logging.error(msg)


            def convert_xml_section_to_json(dir:str, models_path:str, model_types:dict, delete_origin:bool=False):
                """
                The function `convert_xml_section_to_json` converts XML files to JSON format, extracting specific
                data and saving it in a JSON file.
                
                @param dir The `dir` parameter is a string that represents the directory path where the XML files
                are located.
                @param models_path The `models_path` parameter is the path to the directory where the XML and JSON
                files are stored.
                @param model_types The `model_types` parameter is a dictionary that maps the model names to their
                corresponding types. It is used to populate the "tipo" field in the JSON data.
                @param delete_origin The `delete_origin` parameter is a boolean flag that determines whether or not
                to delete the original XML file after converting it to JSON. If `delete_origin` is set to `True`,
                the original XML file will be deleted. If `delete_origin` is set to `False` (default),
                """

                for xmap in glob( path.join(models_path, dir, "map_*.xml") ):
                
                    data = {}

                    model = Path(xmap).stem
                    m = model.split("_")

                    data["nomeModello"] = m[1]
                    data["etichetta"] = model
                    data["dataEmissione"] = datetime.utcfromtimestamp( path.getmtime(xmap) ).replace(tzinfo=pytz.UTC).isoformat(sep="T", timespec="microseconds")
                    data["pubblico"] = True
                    data["tipo"] = model_types.get(m[1], "")
                    data["percorso"] = dir

                    images = []

                    with open(xmap, "r") as f:

                        fdata = f.read()
                        Bs_data = bs4(fdata, features="xml")

                        for tag in Bs_data.find_all('marker'):
                        
                            image = {}

                            image["var"] = tag.get("var")
                            image["title"] = tag.get("title")
                            image["like"] = tag.get("like")
                            image["offset"] = tag.get("offset")
                            image["label"] = tag.get("label")
                    
                            images.append(image)

                    data["immagini"] = images
                            
                    with open( path.join( models_path, dir, "webp", model + ".json" ), "w") as outfile:
                        json.dump(data, outfile, indent = 4)

                    if delete_origin:
                        if path.exists( path.join(models_path, dir, "webp", model + ".json" ) ):
                            remove(xmap) 


            def convert_xml_map_to_json(dir:str, models_path:str, model_types:dict, delete_origin:bool=False):
                """
                The function `convert_xml_map_to_json` converts XML map files to JSON format, saving the converted
                files in a specified directory and optionally deleting the original XML files.
                
                @param dir The `dir` parameter is a string that represents the directory path where the XML files
                are located. It specifies the directory where the XML files are stored.
                @param models_path The `models_path` parameter is the path to the directory where the XML files and
                the JSON files will be stored.
                @param model_types The `model_types` parameter is a dictionary that maps the model names to their
                corresponding types. It is used to populate the "tipo" field in the JSON data.
                @param delete_origin A boolean flag indicating whether to delete the original XML file after
                converting it to JSON. If set to True, the original XML file will be deleted. If set to False, the
                original XML file will be retained.
                """
            
                for xsect in glob( path.join(models_path, dir, "section_*.xml") ):

                    data = {}

                    model = Path(xsect).stem
                    m = model.split("_")

                    data["nomeModello"] = m[1]
                    data["etichetta"] = model
                    data["dataEmissione"] = datetime.utcfromtimestamp( path.getmtime(xsect) ).replace(tzinfo=pytz.UTC).isoformat(sep="T", timespec="microseconds")
                    data["pubblico"] = False
                    data["tipo"] = model_types.get(m[1], "")
                    data["percorso"] = dir

                    images = []

                    with open(xsect, "r") as f:

                        fdata = f.read()
                        Bs_data = bs4(fdata, features="xml")

                        for tag in Bs_data.find_all('marker'):
                    
                            image = {}

                            image["file"] = tag.get("file")
                            image["lat"] = tag.get("lat")
                            image["lon"] = tag.get("lon")
                            image["name"] = tag.get("name")
                            image["nick"] = tag.get("nick")

                            images.append(image)

                    data["immagini"] = images

                    with open( path.join( models_path, dir, "webp", model + ".json" ), "w") as outfile:
                        json.dump(data, outfile, indent = 4)

                    if delete_origin:
                        if path.exists( path.join( models_path, dir, "webp", model + ".json" ) ):
                            remove(xsect) 

                            
            BASEDIR = path.abspath( path.dirname(__file__) )
            MODELS_PATH = path.join(BASEDIR, *scheduler.app.config["MODELS_PATH"]) 

            SIZE = (600, 600)
                    
            MODEL_TYPES={
                "bo08":"meteo",
                "molita15":"meteo",
                "ww3ita":"marino",
                "ww3MED":"marino"
            }

            dirs = [ item for item in listdir(MODELS_PATH) if path.isdir(path.join(MODELS_PATH, item)) ]
            for dir in dirs:
                create_webp(dir, SIZE, MODELS_PATH, delete_origin=True)
                             
                convert_xml_section_to_json(dir=dir, models_path=MODELS_PATH, model_types=MODEL_TYPES, delete_origin=True)

                convert_xml_map_to_json(dir=dir, models_path=MODELS_PATH, model_types=MODEL_TYPES, delete_origin=True)
    except Exception as e:
        msg = f"{ __file__} | Line {e.__traceback__.tb_lineno} | {repr(e)}"
        logging.error(msg)


@scheduler.task(
    "interval",
    id="delete_old_models",
    days=1,
    max_instances=1
)
def delete_old_models():
    """
    """

    try:
        with scheduler.app.app_context():

            BASEDIR = path.abspath( path.dirname(__file__) )
            MODELS_PATH = path.join(BASEDIR, *scheduler.app.config["MODELS_PATH"]) 

            expiration_date = ( datetime.now() - timedelta(days=8) ).strftime("%Y%m%d")

            dirs = [ item for item in listdir(MODELS_PATH) if path.isdir(path.join(MODELS_PATH, item)) ]
            for dir in dirs:
                if dir[0:8] < expiration_date:
                    shutil.rmtree(path.join(MODELS_PATH, dir), ignore_errors=True)
    except Exception as e:
        msg = f"{ __file__} | Line {e.__traceback__.tb_lineno} | {repr(e)}"
        logging.error(msg)