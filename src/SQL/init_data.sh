#!/bin/bash
/bin/rm ~/sdc_db

echo "Create Students"
sqlite3 ~/sdc_db < create_Students.sql
echo "Create Attributes"
sqlite3 ~/sdc_db < create_Attributes.sql
echo "Create StdAttrs"
sqlite3 ~/sdc_db < create_StdAttrs.sql
echo "Create Topics"
sqlite3 ~/sdc_db < create_Topics.sql
echo "Create Courses"
sqlite3 ~/sdc_db < create_Courses.sql
echo "Create Desks"
sqlite3 ~/sdc_db < create_Desks.sql
echo "Create Gropups"
sqlite3 ~/sdc_db < create_Groups.sql
echo "Create IsIn"
sqlite3 ~/sdc_db < create_isIn.sql
echo "Create Params"
sqlite3 ~/sdc_db < create_Params.sql

echo "Populate Students"
sqlite3 ~/sdc_db < insert_Students.sql
echo "Populate Attributes"
sqlite3 ~/sdc_db < insert_Attributes.sql
echo "Populate StdAttrs"
sqlite3 ~/sdc_db < insert_StdAttrs.sql
echo "Populate Topics"
sqlite3 ~/sdc_db < insert_Topics.sql
echo "Populate Courses"
sqlite3 ~/sdc_db < insert_Courses.sql
echo "Populate Desks"
sqlite3 ~/sdc_db < insert_Desks.sql
echo "Populate Groups"
sqlite3 ~/sdc_db < insert_Groups.sql
echo "Populate isIn"
sqlite3 ~/sdc_db < insert_isIn.sql
echo "Populate Params"
sqlite3 ~/sdc_db < insert_Params.sql
