CREATE TABLE Courses (
    IdCourse INTEGER PRIMARY KEY,
    CourseName TEXT,
    IdTopic INTEGER,
    FOREIGN KEY (IdTopic) REFERENCES Topic(IdTopic)
);
