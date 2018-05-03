# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 16:44:26 2018

@author: laksh
"""

from urllib.request import urlopen
from random import randint
import json
import csv
import time
import datetime
import pymysql

jfk_latitude = "40.6413"
jfk_longitude = "-73.7781"

"""Function to open the database connection
"""
def open_db_connection():
    host_name = 'localhost'
    port_number = 3306
    user_name = 'root'
    password = '1234'
    database_name = 'hi'
    connection_object = pymysql.connect(host=host_name, port=port_number, 
                                        user=user_name, passwd=password, db=database_name)
    return connection_object

"""Function to close the database connection
"""
def close_db_connection(connection_object):
    if connection_object is  not None:
        connection_object.commit()
        connection_object.close()
        
def lenDigits(x):
    if x < 10:
        return 1
    return 1 + lenDigits(x / 10)

def convertTimestampToSQLDateTime(value):
    array = value.split("/")
    #print(array[len(array)-1])
    array1=array[len(array)-1].split(" ")
    tim=array1[len(array1)-1].split(":")
    array[len(array)-1]=array1[0]
    dt=array[2]+"-"
    
    nod1=lenDigits(int(array[0]))
    if(nod1==1):
        dt+="0"
    dt+=array[0]+"-"
    nod=lenDigits(int(array[1]))
    if(nod==1):
        dt+="0"
    dt+=array[1]+" "
    
    if(lenDigits(int(tim[0]))==1):
        dt+="0"
    dt+=tim[0]+":"
    dt+=tim[1]+":"
    dt+="00"
    print("))))))))))))))",dt)
    return  dt

connection_object = open_db_connection()
if connection_object is not None:
    print("Success!!")
    
    cursor = connection_object.cursor()
    with open('sample_dataset.csv',"rt", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            latitude = row[9].strip()
            longitude = row[8].strip()
            trip_distance_original = row[4].strip()
            trip_time_original = int(float(row[11].strip()))
            dt=convertTimestampToSQLDateTime(row[1].strip())
            print(longitude)
            print(latitude)
            print(trip_distance_original)
            print(trip_time_original)
            url = "http://router.project-osrm.org/route/v1/driving/"+jfk_longitude+","+jfk_latitude+";"
            if((trip_distance_original!=0) and (latitude !="0") and (longitude !="0") and (trip_time_original!="0")and (trip_time_original!=0)):
                url += longitude + "," + latitude
                response = urlopen(url)
                string = response.read().decode('utf-8')
                json_obj = json.loads(string)
            
                    # trip distance in miles
                trip_distance_from_source = json_obj['routes'][0]['distance'] * float(0.000621371)
                # trip duration in seconds
                trip_duration_from_source = json_obj['routes'][0]['duration']
                print("trip_duration_from_source--->",round(trip_duration_from_source,2))
                # average_speed in miles per second
                average_speed = float(trip_distance_original)/int(trip_time_original)
                willing_to_walk = randint(0,1)
                sql_query_part_one = "insert into ridesharing_trips_new(VendorID,passenger_count,tpep_pickup_datetime,trip_duration_from_source,"
                sql_query_part_two = " trip_distance_original,trip_distance_from_source,dropoff_latitude,dropoff_longitude,original_average_speed,willing_to_walk)"
                sql_query_part_three = " values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                sql_query = sql_query_part_one + sql_query_part_two + sql_query_part_three
                tuple_record=(row[0].strip(),row[3].strip(),dt,round(trip_duration_from_source,2),row[4].strip(), round(trip_distance_from_source,2),latitude,longitude,round(average_speed,2),willing_to_walk)
                    #print("----")
                cursor.execute(sql_query, tuple_record)
                connection_object.commit()
                    
                    
                    
                
           
         
             
               
        cursor.close()
        close_db_connection(connection_object)
        
        
        