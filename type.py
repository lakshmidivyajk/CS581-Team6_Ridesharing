# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 09:14:08 2018

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
        
class Rides:
    def __init__(self, tripID, medallion, passenger_count, tpep_pickup_datetime, trip_duration_from_source, trip_distance_from_source,
                  dropoff_lattitude, dropoff_longitude, willing_to_walk):
        self.trip_id = tripID
        self.medallion = medallion
        self.passenger_count = passenger_count
        self.pickup_datetime = tpep_pickup_datetime
        self.trip_duration_from_source = trip_duration_from_source
        self.trip_distance_from_source = trip_distance_from_source
        self.dropoff_lattitude = dropoff_lattitude
        self.dropoff_longitude = dropoff_longitude
        self.willing_to_walk = willing_to_walk
        

            
                 
  

    

        