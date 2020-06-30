class Desk():
    def __int__(self, id, cx, cy):
        self.__id = id
        self.cx, self.cy = 0, 0

class ModRoom():
    """Room management class"""
    def __init__(self, cursor, name=None):
        self.__name = name
        self.__id = 0
        self.__cursor = cursor

        self.get_id()
        self.fetch_all_desks()


    def get_id(self):
        """Gets the room Id from the name
        If the name does not exist, creates the room"""

        if self.__name is not None:
            req = "SELECT IdRoom FROM Rooms WHERE RoomName = ?"
            self.__cursor.execute(req, self.__name)
            r = self.__cursor.fetchall()
            if len(r) == 0:
                # Room does not exist -> we create it
                rq = "INSERT INTO Rooms (RoomName) VALUES (?)"
                self.__cursor.execute(req, self.__name)
                self.__id = self.__cursor.lastrowid()
            else:
                self.__id = r[0][0]
        else:
            self.__id = 0
    
    def fetch_all_desks(self):
        """fetch all the desks in the room from the BDD"""
        if self.__id is not None:
            req = "SELECT IdDesk, CoordX, CoordY FROM Desks WHERE IdRoom = ?;"
            self.__cursor.execute(req, self.__id)
            r = self.__cursor.fetchall()
            for d in r :
                dsk = Desk(d[0], d[1], d[2])
                self.__all_desks.append(dsk)
    
    def set_name(self, name):
        self.__name = name
        self.get_id()
        self.fetch_all_desks()
    
    def add_desk(self, cx, cy):
        req = "INSERT INTO Desks (CoordX, CoordY) VALUES (?, ?)"
        self.__cursor.execute(req, cx, cy)
        dsk = Desk(self.__cursor.lastrowid, cx, cy)
        self.__all_desks.append(dsk)
    
    def get_desk_id(self, cx, cy):
        req = "SELECT IdDesk FROM Desks WHERE IdRoom = ? AND CoordX = ? AND CoordY = ?"
        self.__cursor.execute(req, self.__id, cx, cy)
        r = self.__cursor.fetchall()
        if len(r) == 0:
            return 0
        else:
            return r[0][0]