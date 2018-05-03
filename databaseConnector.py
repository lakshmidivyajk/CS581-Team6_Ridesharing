# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 09:13:34 2018

@author: laksh
"""

import pymysql

"""Class definition to details of trips
"""

def openConnection():
    host_name = 'localhost'
    port_number = 3306
    user_name = 'root'
    password = '1234'
    database_name = 'hi'
    conn = pymysql.connect(host=host_name, port=port_number, 
                                        user=user_name, passwd=password, db=database_name)
    return conn

"""Function to close the database connection
"""
def closeConnection(conn):
    if conn is  not None:
        conn.commit()
        conn.close()
        