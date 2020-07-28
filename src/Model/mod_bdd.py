from src.Model.mod_types import Desk, Student


class ModBdd():
    """This class deals with SQL requests
    All commits are done by the controller"""

    def __init__(self, bdd):
        self.__bdd = bdd
        self.__cursor = self.__bdd.cursor()
    
    #
    # Courses related requests
    #

    def get_courses(self):
        """Gets all the courses
        Input : 
        Output : list of tuples (course_name, course_id) """

        req = "SELECT IdCourse, CourseName, Topics.TopicName FROM Courses JOIN Topics USING (IdTopic) ORDER BY CourseName"
        self.__cursor.execute(req)
        r = self.__cursor.fetchall()
        result = []
        for c in r:
            result.append((c[0], c[1], c[2]))
        return result

    def get_course_id_by_name(self, name):
        """Gets the course Id from the name
        Input : name - course name
        Output : idCourse or 0 if the name does not exist"""

        req = "SELECT IdCourse FROM Courses WHERE CourseName = ?"
        self.__cursor.execute(req, [name])
        r = self.__cursor.fetchone()
        return 0 if r is None else r[0]
    
    def get_topic_id_by_course_id(self, id_course):
        """Gets the topic Id from the course id
        Input : id_course 
        Output : topic id or 0"""

        req = "SELECT IdTopic FROM Courses WHERE IdCourse = ?"
        self.__cursor.execute(req, [id_course])
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
        Input : id_course - if of the course
                row, col : Corrdinates of the desk
        Output : idDesk or 0 if no desk is present"""

        req = "SELECT IdDesk FROM Desks WHERE IdCourse = ? AND DeskRow = ? AND DeskCol = ?"
        self.__cursor.execute(req, [id_course, row, col])
        r = self.__cursor.fetchone()
        return 0 if r is None else r[0]
    
    def get_desk_by_id(self, id_desk):
        """Returns the desk designed by id_desk
        Input : id_cdesk - if of the desk
        Output : Desk object or None"""

        req = "SELECT * FROM Desks WHERE IdDesk = ?"
        self.__cursor.execute(req, [id_desk])
        r = self.__cursor.fetchone()
        return r if r is None else Desk(r[0], r[1], r[2], r[3], r[4])

    def create_course_with_name(self, name):
        """Creates a new room.
        Input : name - course name
        Output : idCourse 
            if name already exist, idCourse is the id of the existing course
            if name doesn't exist, idCourse is the id of the course just created
        The topic id of the new course is 1 (main topic)"""
        id = self.get_course_id_by_name(name)
        if id == 0:
            req = "INSERT INTO Courses (CourseName, IdTopic) VALUES (?, 1)"
            self.__cursor.execute(req, [name])
            id = self.__cursor.lastrowid
        return id

    def delete_course_with_id(self, course_id):
        """delete a course given its id
        all desks in this course will be deleted too !
        commit must be called separately"""
        
        req = "DELETE FROM Desks WHERE IdCourse = ?"
        self.__cursor.execute(req, [course_id])

        req = "DELETE FROM Courses WHERE IdCourse = ?"
        self.__cursor.execute(req, [course_id])
        
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
            return id_dsk
        else:
            raise ValueError('new_desk error : invalid course id')
            return 0

    def remove_desk_by_id(self, id_desk):
        """Removes a desk
        Input : id_desk
        Output : None"""

        req = "DELETE FROM Desks WHERE IdDesk = ?"
        self.__cursor.execute(req, [id_desk])
        return None

    def move_desk_by_id(self, id_desk, row, col):
        """Moves a desk to a new destination
        Input : id_desk : the id of the desk to move
                row, col : destination
        Output : None"""
        req = "UPDATE Desks SET DeskRow = ?, DeskCol = ?  WHERE IdDesk = ?"
        self.__cursor.execute(req, [row, col, id_desk])
        return None

    def set_student_in_desk_by_id(self, std_id, id_desk):
        """Places a student on a desk/
        Input : std_id : id of student to place
                id_desk : id of the desk
        Output : None"""

        if id_desk != 0:
            req = "UPDATE Desks SET IdStudent = ? WHERE IdDesk = ?"
            self.__cursor.execute (req, [std_id, id_desk])

    #
    # Student relative requests
    #

    def get_groups(self):
        """Returns the group list
        Input : 
        Output : list of group names"""

        req = "SELECT GroupName FROM Groups ORDER BY GroupName"
        self.__cursor.execute(req)
        r = self.__cursor.fetchall()
        return [] if r is None else [ c[0] for c in r ]
    
    def create_group(self, group_name):
        group_id = self.get_group_id_by_name(group_name)
        if group_id != 0:
            return group_id
        else:
            req = "INSERT INTO Groups (GroupName) VALUES (?)"
            self.__cursor.execute(req, [group_name])
            return self.__cursor.lastrowid

    def get_group_id_by_name(self, group_name):
        """Returns the group id
        Input : group_name - group name
        Output : Group id"""

        req = "SELECT IdGroup FROM Groups WHERE GroupName = ?"
        self.__cursor.execute(req, [group_name])
        r = self.__cursor.fetchone()
        return 0 if r is None else r[0]

    def get_group_name_by_id(self, group_id):
        """Returns the group id
        Input : group_id - group id
        Output : Group name"""

        req = "SELECT GroupName FROM Groups WHERE IdGroup = ?"
        self.__cursor.execute(req, [group_id])
        r = self.__cursor.fetchone()
        return "" if r is None else r[0]

    def insert_student_in_group_id(self, firstname, lastname, order, group_id):
        """Create a new student by firstname and lastname in group by id
        return the nbew student id"""

        req = "INSERT INTO Students (StdFirstName, StdLastName, OrderKey) VALUES (?, ?, ?)"
        self.__cursor.execute(req, [firstname, lastname, order])
        std_id = self.__cursor.lastrowid
        req = "INSERT INTO IsIn (IdStudent, IdGroup) VALUES (?, ?)"
        self.__cursor.execute(req, [std_id, group_id])
        return std_id

    def rename_student_by_id(self, std_id, firstname, lastname):
        req = "UPDATE  Students SET StdFirstName = ?, StdLastName = ? WHERE IdStudent = ?"
        self.__cursor.execute(req, [firstname, lastname, std_id])

    def insert_isin(self, std_id, group_id):
        """Insert the student id in the group id"""
        req = "INSERT INTO IsIn (IdStudent, IdGroup) VALUES (?, ?)"
        self.__cursor.execute(req, [std_id, group_id])
    
    def delete_isin(self, std_id, group_id):
        """Delete the student id from the group id"""
        req = "DELETE FROM IsIn WHERE IdStudent = ? AND IdGroup = ?"
        self.__cursor.execute(req, [std_id, group_id])
    
    def nb_groups_contains_student_by_id(self, std_id):
        """Returns the number of groups student std_id belongs to"""
        req = "SELECT COUNT(*) FROM IsIn WHERE IdStudent = ?"
        self.__cursor.execute(req, [std_id])
        r = self.__cursor.fetchone()
        return r[0]

    def delete_student_by_id(self, std_id):
        """Remove a student from the surface of the earth"""
        # Delete Attributes
        req = "DELETE FROM StdAttrs WHERE IdStudent = ?"
        self.__cursor.execute(req, [std_id])
        # Free Desks
        req = "UPDATE Desks SET IdStudent = 0 WHERE IdStudent = ?"
        self.__cursor.execute(req, [std_id])
        # Delete IsIn just to be sure
        req = "DELETE FROM IsIn WHERE IdStudent = ?"
        self.__cursor.execute(req, [std_id])
        # Kill the student
        req = "DELETE FROM Students WHERE IdStudent = ?"
        self.__cursor.execute(req, [std_id])

    def remove_student_from_group(self, std_id, group_id):
        """Remove a student from a group"""
        self.delete_isin(std_id, group_id)
        n = self.nb_groups_contains_student_by_id(std_id)
        # Students belongs to no group
        # He is fired !
        if n == 0:
            self.delete_student_by_id(std_id)

    def get_student_by_id(self, std_id):
        """Returns a Student object
        Input : idStd - student id
        Output : Student object or None of no students matches the idStd"""

        req = "SELECT * FROM Students WHERE IdStudent = ?"
        self.__cursor.execute(req, [std_id])
        r = self.__cursor.fetchone()
        return r if r is None else Student(std_id, r[1], r[2])
        
    def get_students_in_course_by_id(self, id_course):
        """Returns an array of Students in the room
        Input : id_course - the course id
        Output : a list (maybe empty) of students in the course"""
        req = """SELECT * from Students JOIN Desks USING (idStudent) WHERE Desks.IdCourse = ? ORDER BY OrderKey"""
        self.__cursor.execute(req, [id_course])
        r = self.__cursor.fetchall()
        return [] if r is None else [Student(t[0], t[1], t[2]) for t in r ]

    def get_students_in_group(self, group_name):
        """Returns an array of Students in a group
        Input : group_name - the group name
        Output : a list (maybe empty) of students in the group"""
        req = """SELECT * from Students JOIN IsIn USING (idStudent) JOIN Groups USING (IdGroup) WHERE Groups.GroupName = ? ORDER BY OrderKey"""
        self.__cursor.execute(req, [group_name])
        r = self.__cursor.fetchall()
        return [] if r is None else [Student(t[0], t[1], t[2]) for t in r ]

    def get_student_by_desk_id(self, id_desk):
        """Returns the Id of the desk at the given coordinates
        Input : id_desk - id of the desk
        Output : student object or None"""

        req = "SELECT * FROM Students JOIN Desks USING (IdStudent) WHERE Desks.IdDesk = ?"
        self.__cursor.execute(req, [id_desk])
        r = self.__cursor.fetchone()
        return r if r is None else Student(r[0], r[1], r[2])
    
    def update_student_order_with_id(self, idS, order):
            req = "UPDATE Students SET OrderKey = ? WHERE IdStudent = ?"
            self.__cursor.execute (req, [order, idS])
    
    def delete_group_by_id(self, group_id):
        """Delete a all students in a group then the group itself
        Commit must be done separately
        Input : group_id : Id of the group to delete
        """
        students = self.get_students_in_group(self.get_group_name_by_id(group_id))
        # Delete all students in the group
        # If a student belongs to another group he will survive
        for std in students:
            self.remove_student_from_group(std.id, group_id)
        # removes the group
        req = "DELETE FROM Groups WHERE IdGroup = ?"
        self.__cursor.execute(req, [group_id])
    #
    # Topic relative requests
    #
    def get_topic_from_course_id(self, id_course):
        """Returns a Student object
        Input : id_course - course id
        Output : topic name or '' """

        req = "SELECT TopicName FROM Topics JOIN Courses USING (IdTopic) WHERE Courses.IdCourse = ?"
        self.__cursor.execute(req, [id_course])
        r = self.__cursor.fetchone()
        return "" if r is None else r[0]

    def get_topics_names(self):
        """Returns a Student object"""

        req = "SELECT TopicName FROM Topics"
        self.__cursor.execute(req)
        r = self.__cursor.fetchall()
        return ["Cueillette de fraises"] if r is None else [ t[0] for t in r ]
    
    def set_topic_to_course_id(self, id_course, new_topic):
        req = "UPDATE Courses SET IdTopic = ( SELECT Topics.IdTopic FROM Topics WHERE Topics.TopicName = ? ) WHERE IdCourse = ?"
        self.__cursor.execute(req, [new_topic, id_course])
    
    #
    # Attributes relative requests
    #

    def get_all_attributes(self):
        """Returns a list of all attributes
        format : [ (id1, attrName1, attrType1), (...), ...]"""

        req = "SELECT * FROM Attributes"
        self.__cursor.execute(req)
        r = self.__cursor.fetchall()
        return [] if r is None else [ (t[0], t[1], t[2]) for t in r ]
    
    def insert_attribute(self, attr_name, attr_type):
        """Create a new attribute
        return the new attribute id
        commit must be called separately"""

        req = "INSERT INTO Attributes (AttrName, AttrType) VALUES (?, ?)"
        self.__cursor.execute(req, [attr_name, attr_type])
        attr_id = self.__cursor.lastrowid
        return attr_id
    
    def delete_attribute_with_id(self, attr_id):
        """delete an attribute given its id
        all students attributes will be deleted too !
        commit must be called separately"""
        
        req = "DELETE FROM StdAttrs WHERE IdAttr = ?"
        self.__cursor.execute(req, [attr_id])

        req = "DELETE FROM Attributes WHERE IdAttr = ?"
        self.__cursor.execute(req, [attr_id])
    
    def get_attribute_value(self, id_std, id_attr, id_topic):
        req = "SELECT stdAttrValue FROM StdAttrs WHERE IdStudent = ? AND IdAttr = ? AND IdTopic = ?"
        self.__cursor.execute(req, [id_std, id_attr, id_topic])
        r = self.__cursor.fetchone()
        return "" if r is None else r[0]

    def get_attribute_type_from_id(self, id_attr):
        req = "SELECT AttrType FROM Attributes WHERE IdAttr = ?"
        self.__cursor.execute(req, [id_attr])
        r = self.__cursor.fetchone()
        return "" if r is None else r[0]

    def update_attr_with_ids(self, id_std, id_attr, id_topic, val):
        """Insert or update Value as an attribute value
        commit must be done separately
        """
        req = "SELECT IdStdAttr FROM StdAttrs WHERE IdStudent = ? AND IdAttr = ? AND IdTopic = ?"
        self.__cursor.execute(req, [id_std, id_attr, id_topic])
        r = self.__cursor.fetchone()
        if r is None:
            # Insert new value in the BDD
            req = "INSERT INTO StdAttrs (StdAttrValue, IdStudent, IdAttr, IdTopic) VALUES (?, ?, ?, ?)"
            self.__cursor.execute(req, [val, id_std, id_attr, id_topic])
        else:
            req = "UPDATE StdAttrs SET StdAttrValue = ? WHERE IdStdAttr = ?"
            self.__cursor.execute(req, [val, r[0]])
