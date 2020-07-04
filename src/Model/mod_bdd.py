from src.Model.mod_types import Desk, Student


class ModBdd():
    """This class deals with SQL requests"""

    def __init__(self, bdd):
        self.__bdd = bdd
        self.__cursor = self.__bdd.cursor()
    
    #
    # Room related requests
    #
    def get_course_id_by_name(self, name):
        """Gets the course Id from the name
        Input : name - course name
        Output : idCourse or 0 if the name does not exist"""

        req = "SELECT IdCourse FROM Courses WHERE CourseName = ?"
        self.__cursor.execute(req, [name])
        r = self.__cursor.fetchone()
        return 0 if r is None else r[0]

    def get_course_all_desks(self, id_course):
        """fetch all the desks in the course
        input : id - id of the course
        output: an array of desks"""
        all_desks = []
        if id_course != 0:
            req = "SELECT * FROM Desks WHERE IdCourse = ?;"
            self.__cursor.execute(req, [id_course])
            r = self.__cursor.fetchall()
            for d in r:
                dsk = Desk(d[0], d[1], d[2], d[3], d[4])
                all_desks.append(dsk)
        return all_desks

    def get_desk_id_in_course_by_coords(self, id_course, row, col):
        """Returns the Id of the desk at the given coordinates
        Input : idCourse - if of the course
                row, col : Corrdinates of the desk
        OUtput : idDesk or 0 if no desk is present"""

        req = "SELECT IdDesk FROM Desks WHERE IdCourse = ? AND DeskRow = ? AND DeskCol = ?"
        self.__cursor.execute(req, [id_course, row, col])
        r = self.__cursor.fetchone()
        return 0 if r is None else r[0]

    def create_course_with_name(self, name):
        """Creates a new room.
        Input : name - course name
        Output : idCourse 
            if name already exist, idCourse is the id of the existing course
            if name doesn't exist, idCourse is the id of the course just created
        If the name exists already, just return the room id"""
        id = self.get_course_id_by_name(name)
        if id == 0:
            req = "INSERT INTO Rooms (CourseName) VALUES (?)"
            self.__cursor.execute(req, [name])
            id = self.__cursor.lastrowid
            self.__bdd.commit()
        return id
    
    def create_new_desk_in_course(self, row, col, id_course):
        """Creates a new desk in a course
        Input : idcourse - course id
                cx, cy : coordinates of the desk
        Output : the desk id 
        The student Id is set to 0"""
        if id_course != 0:
            req = "INSERT INTO Desks (DeskRow, DeskCol, IdCourse, IdStudent) VALUES (?, ?, ?, ?)"
            self.__cursor.execute(req, [row, col, id_course, 0])
            id_dsk = self.__cursor.lastrowid
            dsk = Desk(id_dsk, row, col, id_course, 0)
            self.__bdd.commit()
            return id_dsk
        else:
            raise ValueError('new_desk error : invalid course id')
            return 0
    
    #
    # Student relative requests
    #
    def get_student_by_id(self, id_std):
        """Returns a Student object
        Input : idStd - student id
        Output : Student object or None of no students matches the idStd"""

        req = "SELECT * FROM Students WHERE IdStudent = ?"
        self.__cursor.execute(req, [id_std])
        r = self.__cursor.fetchone()
        return r if r is None else Student(id, r[1], r[2])
        
    def get_students_in_course(self, id_course):
        """Returns an array of Students in the room
        Input : id_course - the course id
        Output : a list (maybe empty) of students in the course"""
        req = """SELECT * from Students JOIN Desks ON (idStudent) WHERE Desks.IdCourse = ?"""
        self.__cursor.execute(req, id_course)
        r = self.__cursor.fetchall()
        return [] if r is None else [Student(t[0], t[1], t[2]) for t in r ]
