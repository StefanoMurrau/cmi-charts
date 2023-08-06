from app.database import db
import json
from app.models import Actions
from flask_seeder import Seeder
from os import path


BASEDIR = path.abspath(path.dirname(__file__))


class ActionsSeeder(Seeder):
    """
    This class is a subclass of the Seeder class, which is a subclass of the Flask-Script class. 
    The ActionsSeeder class is a custom class that I created to help me seed my database with Actions data. 
    """

    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 10


    def run(self):
        with open(path.join(BASEDIR, "json", "actions.json"), "r") as j:
            data = json.load(j)

        for d in data: 
            action = Actions(id=d["id"], name=d["name"], description=d["description"])
            self.db.session.add(action)
            