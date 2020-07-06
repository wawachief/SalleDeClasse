CREATE TABLE Attributes (
    IdAttr INTEGER PRIMARY KEY,
    AttrName TEXT,
    IdAttrType INTEGER,
    FOREIGN KEY (IdAttrType) REFERENCES AttrTypes(IdAttrType)
);
