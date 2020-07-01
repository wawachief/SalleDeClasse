class Student():
    def __init__(self, id=0, name="", surname=""):
        self.id = id
        self.name = name
        self.surname = surname

class ModStudents():
    def __init__(self, bdd):
        self.__bdd = bdd
        self.__cursor = self.__bdd.cursor()
    
    def get_student_by_id(self, id):
        req = "SELECT * FROM Students WHERE IdStudent = ?"
        self.__cursor.execute(req, self.id)
        r = self.__cursor.fetchone()
        if r is  None:
            return None
        else:
            return Student(id, r[0], r[1])
        
    def students_in_room(self, id_room):
        """Returns an array of Students in the room"""
        req = """SELECT * from Students JOIN RelStdDsk ON (idStudent) JOIN Desks ON (IdDesk) WHERE Desks.IdRoom = ?"""
        self.__cursor.execute(req, id_room)
        r = self.__cursor.fetchall()
        return [Student(t[0], t[1], t[2]) for t in r ]