class Desk:
    def __init__(self, idd, row, col, id_course, id_student):
        self.id = idd
        self.row, self.col = row, col
        self.id_course = id_course
        self.id_student = id_student
    
    def __str__(self):
        status = "Free" if self.id_student == 0 else "Occupied"
        return f"Desk [{self.row} - {self.col} ] Course {self.id_course} - {status}"


class Student:
    def __init__(self, ids=0, firstname="", lastname=""):
        self.id = ids
        self.firstname = firstname
        self.lastname = lastname

    def __str__(self):
        return f"{self.lastname} {self.firstname} ({self.id})"
