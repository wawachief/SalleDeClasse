CREATE TABLE StdAttrs (
    IdStdAttr INTEGER PRIMARY KEY,
    StdAttrValue TEXT,
    IdAttr INTEGER,
    IdStudent INTEGER,
    IdTopic INTEGER,
    FOREIGN KEY (IdAttr) REFERENCES Attributes(IdAttr),
    FOREIGN KEY (IdStudent) REFERENCES Students(IdStudent),
    FOREIGN KEY (IdTopic) REFERENCES Topics(IdTopic)
);