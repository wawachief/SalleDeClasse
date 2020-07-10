CREATE TABLE Attributes (
    IdAttr INTEGER PRIMARY KEY,
    AttrName VARCHAR(30),
    IdAttrType INTEGER,
    FOREIGN KEY (IdAttrType) REFERENCES AttrTypes(IdAttrType)
);
