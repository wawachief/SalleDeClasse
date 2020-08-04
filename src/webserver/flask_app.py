import sqlite3

from PySide2.QtCore import QThread
from flask import Flask, render_template, request, jsonify
from src.Controllers.main_controller import MainController
from src.Model.mod_bdd import ModBdd
from flask_socketio import SocketIO

flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'secret!'
socket_io = SocketIO(flask_app)
controller: MainController = None
clients = []


@flask_app.route('/')
def load_app():
    active_course = controller.id_course
    mod_bdd = get_bdd_connection()
    active_course_name = mod_bdd.get_course_name_by_id(active_course)
    students = mod_bdd.get_students_in_course_by_id(active_course)
    print(students)
    return render_template('template_v2.html', titre="Liste des élèves de la classe " + active_course_name,
                           students=students)


@flask_app.route('/api/student')
def select_student():
    student_id = int(request.args.get('id', 0))
    selected = request.args.get('selected', 0) == "true"
    controller.sig_flask_desk_selection_changed.emit(student_id, selected)
    resp = jsonify(success=True)
    return resp


@socket_io.on('connect')
def handle_connect():
    print('Client connected')
    clients.append(request.sid)


@socket_io.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    clients.remove(request.sid)


@socket_io.on('confirm_connect')
def confirm_connection_event(json):
    print('received json: ' + str(json))
    mod_bdd = get_bdd_connection()
    ids = controller.v_canvas.get_selected_tiles()
    for desk_id in ids:
        student = mod_bdd.get_student_by_desk_id(desk_id)
        select_student(student.id, True)
        print("selected students : " + str(student.id))


@socket_io.on('selection_changed')
def on_selection_changed(json):
    print('selection changed: ' + str(json))
    select_student(json['id'], json['selected'])


def select_student(student_id: int, selected: bool):
    socket_io.emit('select_student', {"id": student_id, "selected": selected})


def get_bdd_connection():
    bdd = sqlite3.connect("src/SQL/sdc_db")
    return ModBdd(bdd)


class FlaskThread(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.start()

    def run(self):
        socket_io.run(flask_app, host='0.0.0.0')

    def init_controller(self, controller_param):
        global controller
        controller = controller_param
