class Desk:
    def __init__(self, id, cx, cy):
        self.id = id
        self.cx, self.cy = cx, cy
    
    def __str__(self):
        return f"Desk [{self.cx} - {self.cy} ]"

class Student():
    def __init__(self, id=0, name="", surname=""):
        self.id = id
        self.name = name
        self.surname = surname
