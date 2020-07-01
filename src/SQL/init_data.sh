#!/bin/bash
/bin/rm sdc_db

sqlite3 sdc_db < create_Students.sql
sqlite3 sdc_db < create_Rooms.sql
sqlite3 sdc_db < create_Desks.sql
sqlite3 sdc_db < create_RelStdDsk.sql

sqlite3 sdc_db < insert_Students.sql
sqlite3 sdc_db < insert_RelStdDsk.sql
