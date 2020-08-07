import sqlite3

from PySide2.QtCore import QThread
from flask import Flask, render_template, request, jsonify
from src.Controllers.main_controller import MainController
from src.Model.mod_bdd import ModBdd
from flask_socketio import SocketIO
from random import choice
import os, signal

flask_thread = None
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'secret!'
socket_io = SocketIO(flask_app, logger=True, async_mode="eventlet", engineio_logger=True)
controller: MainController = None
clients = []


@flask_app.route('/')
def load_app():
    active_course = controller.id_course
    mod_bdd = get_bdd_connection()
    active_course_name = mod_bdd.get_course_name_by_id(active_course)
    students = mod_bdd.get_students_in_course_by_id(active_course)
    return render_template('salle_de_classe.html', titre="Liste des élèves de la classe " + active_course_name,
                           students=students)


@flask_app.route('/mobile')
def load_app_mobile():
    active_course = controller.id_course
    mod_bdd = get_bdd_connection()
    active_course_name = mod_bdd.get_course_name_by_id(active_course)
    students = mod_bdd.get_students_in_course_by_id(active_course)
    return render_template('salle_de_classe_mobile.html', titre="Liste des élèves de la classe " + active_course_name,
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


@socket_io.on('stop-server')
def stop_server():
    print('Stopping server')
    controller.flask_server.stop_flask()
    # socket_io.stop()
    os.kill(os.getpid(), signal.SIGABRT)
    print("Stopped socketio")


@socket_io.on('confirm_connect')
def confirm_connection_event(json):
    print('received json: ' + str(json))
    mod_bdd = get_bdd_connection()
    ids = controller.v_canvas.get_selected_tiles()
    for desk_id in ids:
        student = mod_bdd.get_student_by_desk_id(desk_id)
        send_student_selection(student.id, True)
        print("selected students : " + str(student.id))


@socket_io.on('selection_changed')
def on_selection_changed(json):
    print('selection changed: ' + str(json))
    send_student_selection(json['id'], json['selected'])


@socket_io.on('random_selection')
def random_selection_request():
    print('Random Selection requested')
    mod_bdd = get_bdd_connection()
    desks_id = controller.course_ctrl.get_unselected_occupied_desks_id(bdd=mod_bdd)
    if desks_id:
        # should be always be true otherwise the hutton is disabled
        desk_id = choice(desks_id)
        student = mod_bdd.get_student_by_desk_id(desk_id)
        controller.sig_flask_desk_selection_changed.emit(student.id, True)
        send_student_selection(student.id, True)


def send_student_selection(student_id: int, selected: bool):
    socket_io.emit('select_student', {"id": student_id, "selected": selected})


def get_bdd_connection():
    bdd = sqlite3.connect("src/SQL/sdc_db")
    return ModBdd(bdd)


class FlaskThread(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.start()

    def run(self):
        socket_io.run(flask_app, port=5000, host='0.0.0.0')

    def init_controller(self, controller_param):
        global controller
        controller = controller_param
        controller.flask_server = self

    def stop_flask(self):
        self.exit()
