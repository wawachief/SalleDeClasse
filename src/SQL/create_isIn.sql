CREATE TABLE IsIn (
    IdStudent INTEGER,
    IdGroup INTEGER,
    FOREIGN KEY (IdStudent) REFERENCES Students(IdStudent)
    FOREIGN KEY (IdGroup) REFERENCES Classes(IdGroup)
);