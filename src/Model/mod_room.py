class Desk:
    def __init__(self, id, cx, cy):
        self.id = id
        self.cx, self.cy = cx, cy
    
    def __str__(self):
        return f"Desk [{self.cx} - {self.cy} ]"


class ModRoom:
    """Room management class"""
    def __init__(self, bdd, name=None):
        self.__name = name
        self.id = 0
        self.__bdd = bdd
        self.__cursor = self.__bdd.cursor()
        self.__all_desks = []

        self.get_id()

    def get_id(self):
        """Gets the room Id from the name
        If the name does not exist, creates the room"""

        if self.__name is not None:
            req = "SELECT IdRoom FROM Rooms WHERE RoomName = ?"
            self.__cursor.execute(req, [self.__name])
            r = self.__cursor.fetchall()
            if len(r) == 0:
                # Room does not exist -> we create it
                req = "INSERT INTO Rooms (RoomName) VALUES (?)"
                self.__cursor.execute(req, [self.__name])
                self.id = self.__cursor.lastrowid
                self.__bdd.commit()
            else:
                self.id = r[0][0]
        else:
            self.id = 0
    
    def get_all_desks(self):
        """fetch all the desks in the room from the BDD"""
        if self.id is not None:
            all_desks = []
            req = "SELECT IdDesk, CoordX, CoordY FROM Desks WHERE IdRoom = ?;"
            self.__cursor.execute(req, [self.id])
            r = self.__cursor.fetchall()
            for d in r :
                dsk = Desk(d[0], d[1], d[2])
                all_desks.append(dsk)
            return all_desks
        return []
    
    def set_name(self, name):
        self.__name = name
        self.get_id()
    
    def add_desk(self, cx, cy):
        if self.id != 0:
            req = "INSERT INTO Desks (IdRoom, CoordX, CoordY) VALUES (?, ?, ?)"
            self.__cursor.execute(req, [self.id, cx, cy])
            id_dsk = self.__cursor.lastrowid
            dsk = Desk(id_dsk, cx, cy)
            self.__bdd.commit()
            return id_dsk
        else:
            print ('add desk impossible')
            return 0
    
    def get_desk_id(self, cx, cy):
        req = "SELECT IdDesk FROM Desks WHERE IdRoom = ? AND CoordX = ? AND CoordY = ?"
        self.__cursor.execute(req, [self.id, cx, cy])
        r = self.__cursor.fetchall()
        if len(r) == 0:
            return 0
        else:
            return r[0][0]
