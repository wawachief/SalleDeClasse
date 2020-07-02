from src.Model.mod_types import Desk, Student

class ModBdd():
    """This class deals with SQL requests"""

    def __init__(self, bdd):
        self.__bdd = bdd
        self.__cursor = self.__bdd.cursor()
    
    #
    # Room related requests
    #
    def get_room_id_by_name(self, name):
        """Gets the room Id from the name
        If the name does not exist, returns 0"""

        req = "SELECT IdRoom FROM Rooms WHERE RoomName = ?"
        self.__cursor.execute(req, [name])
        r = self.__cursor.fetchone()
        return None if r is None else r[0]

    def get_room_all_desks(self, id):
        """fetch all the desks in the room
        returns an array of desks"""
        all_desks = []
        if id != 0:
            req = "SELECT IdDesk, CoordX, CoordY FROM Desks WHERE IdRoom = ?;"
            self.__cursor.execute(req, [self.id])
            r = self.__cursor.fetchall()
            for d in r :
                dsk = Desk(d[0], d[1], d[2])
                all_desks.append(dsk)
        return all_desks

    def get_desk_id_in_room_by_coords(self, idroom, cx, cy):
        """Returns the Id of the desk at the given coordinates"""
        req = "SELECT IdDesk FROM Desks WHERE IdRoom = ? AND CoordX = ? AND CoordY = ?"
        self.__cursor.execute(req, [idroom, cx, cy])
        r = self.__cursor.fetchone()
        if r is None:
            return 0
        else:
            return r[0]

    def create_room_with_name(self, name):
        """Creates a new room. 
        If the name exists already, just return the room id"""
        id = self.get_room_id_by_name(name)
        if id == 0:
            req = "INSERT INTO Rooms (RoomName) VALUES (?)"
            self.__cursor.execute(req, [name])
            id = self.__cursor.lastrowid
            self.__bdd.commit()
        return id
    
    def create_new_desk_in_room(self, idroom, cx, cy):
        """Creates a new desk in the room identified by idroom
        returns the desk id or 0 """
        if idroom != 0:
            req = "INSERT INTO Desks (IdRoom, CoordX, CoordY) VALUES (?, ?, ?)"
            self.__cursor.execute(req, [idroom, cx, cy])
            id_dsk = self.__cursor.lastrowid
            dsk = Desk(id_dsk, cx, cy)
            self.__bdd.commit()
            return id_dsk
        else:
            print ('add desk impossible')
            return 0
    
    #
    # Student relative requests
    #
    def get_student_by_id(self, id):
        req = "SELECT * FROM Students WHERE IdStudent = ?"
        self.__cursor.execute(req, id)
        r = self.__cursor.fetchone()
        return r if r is None else Student(id, r[0], r[1])
        
    def get_students_in_room(self, id_room):
        """Returns an array of Students in the room"""
        req = """SELECT * from Students JOIN RelStdDsk ON (idStudent) JOIN Desks ON (IdDesk) WHERE Desks.IdRoom = ?"""
        self.__cursor.execute(req, id_room)
        r = self.__cursor.fetchall()
        return r if r is None else [Student(t[0], t[1], t[2]) for t in r ]