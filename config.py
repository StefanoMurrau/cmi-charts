from __future__ import with_statement
import sys
from datetime import timedelta
from os import getenv, path
from dotenv import load_dotenv
from app.functions import get_translation, slugify


BASEDIR = path.abspath(path.dirname(__file__))
ENV_PATH = path.join(BASEDIR, "instance", ".env")


get_translation("config", path.join(BASEDIR, "translations", "locale"), "it")


try:
    with open( ENV_PATH, "r"):
        load_dotenv(ENV_PATH)
except Exception as e:
    msg = f"{ __file__} | Line {e.__traceback__.tb_lineno} | {repr(e)} | In case of a new installation, rename the .env_example file to .env, move it into the instance folder and configure it"
    sys.exit(msg)


class LogFilter(object):
    """
    It's a filter that only allows log records 
    with a specific level to pass through
    """
    
    def __init__(self,level:list):
        self.__level = level

    def filter(self, logRecord:object) ->object:
        """
        If the logRecord.levelno is in the self.__level list, then return the logRecord.levelno and the
        logRecord.module is not equal to "_internal"
        
        @param logRecord The LogRecord object that is being filtered.
        @return The logRecord.levelno and (logRecord.module!="_internal")
        """

        if logRecord.levelno in self.__level:
            return logRecord.levelno and (logRecord.module!="_internal")


class WerkzeugFilter(object):
    """
    It's a filter that returns true 
    if the logRecord.name is "werkzeug"
    """
    
    def filter(self, logRecord:object) -> object:
        """
        It returns True if the logRecord.name is "werkzeug" and False otherwise
        
        @param logRecord The LogRecord object that is being filtered.
        @return The logRecord.name is being returned.
        """
        
        return (logRecord.name=="werkzeug")


class Config(object):
    VERSION = "1.0.0"
    PROJECT_NAME = "cmi_charts"
    DISPLAY_NAME = _("CMI_CHARTS")
    CSRF_ENABLED = True
    APP_HOST = '0.0.0.0'
    APP_PORT = "4040"
    APP_SSL_CONTEXT = ["./certs/server.crt", "./certs/server.key"]
    JSON_SORT_KEYS = False
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    SESSION_FILE_THRESHOLD = 1
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    ADMIN_NAME = getenv('ADMIN_NAME')
    ADMIN_MAIL = getenv('ADMIN_MAIL')
    MAIL_USE_TLS = True
    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": True,
        "filters": {
            "info": {
                '()': LogFilter,
                'level': [20]
            },
            "warning": {
                '()': LogFilter,
                'level': [30,40,50]
            },
            "critical": {
                '()': LogFilter,
                'level': [50]
            },
            "werkzeug": {
                '()': WerkzeugFilter,
            }
        },
        "formatters": {"default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s ( %(pathname)s | line %(lineno)s ): %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        }},
        "handlers": {
            "error.handler": {
                "level": 'WARNING',
                "class": "logging.handlers.RotatingFileHandler",
                "filters": ["warning"],
                "maxBytes": 10000000,
                "filename": "log/error.log",
                "backupCount": 5,
                "formatter": "default"
            },
            "action.handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "filters": ["info"],
                "maxBytes": 10000000,
                "filename": "log/action.log",
                "backupCount": 5,
                "formatter": "default"
            },
            "werkzeug.handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "filters": ["werkzeug"],
                "maxBytes": 10000000,
                "filename": "log/werkzeug.log",
                "backupCount": 5,
                "formatter": "default"
            },
            "critical.handler": {
                "class": "logging.handlers.SMTPHandler",
                "level": "CRITICAL",
                "filters": ["critical"],
                "formatter": "default",
                "mailhost": ( getenv("MAIL_SERVER"), getenv("MAIL_SERVER_PORT")),
                "secure": (),
                "fromaddr":  getenv("ADMIN_MAIL"),
                "toaddrs": [getenv("MAIL_ADDRESS_TO")],
                "credentials": [getenv("MAIL_USER"), getenv("MAIL_PASSWORD")],
                "subject": DISPLAY_NAME +" - ERRORE CRITICO",
            },
        },
        "root":{ 
            "level": "INFO",
            "handlers": ["action.handler", "error.handler", "critical.handler", "werkzeug.handler"],
            "propagate": False,
        },
    }


class ProductionConfig(Config):
    APPLICATION_ROOT = f"/{slugify(Config.DISPLAY_NAME)}"
    ENV = "production"
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    MODELS_PATH = ["static", "data", "models"]
    SECRET_KEY = getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"{getenv('POSTGRES_DB_DRIVER')}://{getenv('POSTGRES_DB_USER')}:{getenv('POSTGRES_DB_PASSWORD')}@{getenv('POSTGRES_DB_URL')}:{getenv('POSTGRES_DB_PORT')}/{Config.PROJECT_NAME}"

    
class DevelopmentConfig(Config):
    APPLICATION_ROOT = f"/"
    ENV = "development"
    SECRET_KEY = "dev"
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    MODELS_PATH = ["static", "data", "models"]
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + path.join(BASEDIR, "instance", Config.PROJECT_NAME + ".db")


class TestingConfig(Config):
    APPLICATION_ROOT = f"/{slugify(Config.DISPLAY_NAME)}/"
    ENV = "development"
    SECRET_KEY = "test"
    DEBUG = True
    TESTING = True
    SESSION_COOKIE_SECURE = True
    MODELS_PATH = ["static", "data", "models"]
    SQLALCHEMY_DATABASE_URI = f"{getenv('POSTGRES_DB_DRIVER')}://{getenv('POSTGRES_DB_USER')}:{getenv('POSTGRES_DB_PASSWORD')}@{getenv('POSTGRES_DB_URL')}:{getenv('POSTGRES_DB_PORT')}/{Config.PROJECT_NAME}"
    
