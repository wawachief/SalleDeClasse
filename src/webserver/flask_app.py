import sqlite3

from PySide2.QtCore import QThread
from flask import Flask, render_template
from src.controller import Controller
from src.Model.mod_bdd import ModBdd

flask_app = Flask(__name__)

controller: Controller = None


@flask_app.route('/')
def hello_world():
    active_course = controller.id_course
    mod_bdd = get_bdd_connection()
    active_course_name = mod_bdd.get_course_name_by_id(active_course)
    students = mod_bdd.get_students_in_course_by_id(active_course)
    print(students)
    return render_template('template.html', titre="Liste des élèves de la classe "+active_course_name, mots=students)


def get_bdd_connection():
    bdd = sqlite3.connect("src/SQL/sdc_db")
    return ModBdd(bdd)


class FlaskThread(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.start()

    def run(self):
        flask_app.run()

    def init_controller(self, controller_param):
        global controller
        controller = controller_param
