CREATE TABLE Desks (
    IdDesk INTEGER PRIMARY KEY,
    DeskRow INTEGER,
    DeskCol INTEGER,
    IdCourse INTEGER,
    IdStudent INTEGER,
    FOREIGN KEY (IdCourse) REFERENCES Rooms(IdCourse)
    FOREIGN KEY (IdStudent) REFERENCES Students(IdStudent)
);