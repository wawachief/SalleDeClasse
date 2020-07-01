CREATE TABLE RelStdDsk (
    IdStudent INTEGER,
    IdDesk INTEGER,
    FOREIGN KEY(IdStudent) REFERENCES Students(IdStudent), 
    FOREIGN KEY(IdDesk) REFERENCES Desks(IdDesk)
)