#!/bin/bash
/bin/rm sdc_db

echo "Create Students"
c:\sqlite\sqlite3 sdc_db < create_Students.sql
echo "Create AttrTypes"
c:\sqlite\sqlite3 sdc_db < create_AttrTypes.sql
echo "Create Attributes"
c:\sqlite\sqlite3 sdc_db < create_Attributes.sql
echo "Create StdAttrs"
c:\sqlite\sqlite3 sdc_db < create_StdAttrs.sql
echo "Create Topics"
c:\sqlite\sqlite3 sdc_db < create_Topics.sql
echo "Create Courses"
c:\sqlite\sqlite3 sdc_db < create_Courses.sql
echo "Create Desks"
c:\sqlite\sqlite3 sdc_db < create_Desks.sql
echo "Create Gropups"
c:\sqlite\sqlite3 sdc_db < create_Groups.sql
echo "Create IsIn"
c:\sqlite\sqlite3 sdc_db < create_isIn.sql

echo "Populate Students"
c:\sqlite\sqlite3 sdc_db < insert_Students.sql
echo "Populate AttrTypes"
c:\sqlite\sqlite3 sdc_db < insert_AttrTypes.sql
echo "Populate Attributes"
c:\sqlite\sqlite3 sdc_db < insert_Attributes.sql
echo "Populate StdAttrs"
c:\sqlite\sqlite3 sdc_db < insert_StdAttrs.sql
echo "Populate Topics"
c:\sqlite\sqlite3 sdc_db < insert_Topics.sql
echo "Populate Courses"
c:\sqlite\sqlite3 sdc_db < insert_Courses.sql
echo "Populate Desks"
c:\sqlite\sqlite3 sdc_db < insert_Desks.sql
echo "Populate Groups"
c:\sqlite\sqlite3 sdc_db < insert_Groups.sql
echo "Populate isIn"
c:\sqlite\sqlite3 sdc_db < insert_isIn.sql
