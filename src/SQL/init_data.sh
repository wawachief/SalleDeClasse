#!/bin/bash
/bin/rm sdc_db

echo "Create Students"
sqlite3 sdc_db < create_Students.sql
echo "Create Courses"
sqlite3 sdc_db < create_Courses.sql
echo "Create Desks"
sqlite3 sdc_db < create_Desks.sql
echo "Create Classes"
sqlite3 sdc_db < create_Classes.sql
echo "Create IsIn"
sqlite3 sdc_db < create_isIn.sql

echo "Populate Students"
sqlite3 sdc_db < insert_Students.sql
echo "Populate Courses"
sqlite3 sdc_db < insert_Courses.sql
echo "Populate Desks"
sqlite3 sdc_db < insert_Desks.sql
echo "Populate Classes"
sqlite3 sdc_db < insert_Classes.sql
echo "Populate isIn"
sqlite3 sdc_db < insert_isIn.sql
