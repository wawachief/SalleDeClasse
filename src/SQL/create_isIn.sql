CREATE TABLE IsIn (
    IdStudent INTEGER,
    IdClass INTEGER,
    FOREIGN KEY (IdStudent) REFERENCES Students(IdStudent)
    FOREIGN KEY (IdClass) REFERENCES Classes(IdClass)
);