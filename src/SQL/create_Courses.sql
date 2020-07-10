CREATE TABLE Courses (
    IdCourse INTEGER PRIMARY KEY,
    CourseName VARCHAR(30),
    IdTopic INTEGER,
    FOREIGN KEY (IdTopic) REFERENCES Topic(IdTopic)
);
