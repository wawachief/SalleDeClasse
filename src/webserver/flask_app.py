from PySide2.QtCore import QThread
from flask import Flask, render_template

flask_app = Flask(__name__)


@flask_app.route('/')
def hello_world():
    mots = ["dans", "Salle","de", "Classe."]
    return render_template('template.html', titre="Bienvenue !", mots=mots)


class FlaskThread(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.start()

    def run(self):
        flask_app.run()
