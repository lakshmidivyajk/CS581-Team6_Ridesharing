# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 10:18:33 2018

@author: laksh
"""
import type
import databaseConnector
from urllib.request import urlopen
import pymysql
import json
import math
import datetime
import numpy as np
import networkx as nx
from math import cos, sin, atan2, radians, degrees

from datetime import timedelta
import time




JFK_lat = "40.6413"
JFK_long = "-73.7781"



mergeable_trips_list = []
metadata_trips_merged = dict()
possible_distance_merged = dict()
ip_trips_for_algorithm = set()
ip_trips_for_maxMatching = set()
dist_dict = dict()
match_dict= dict()
total_number_trips_saved= 0
tnor=0
number_of_pools=0
total_entire_distance=0
total_savedDistance=0
total_unmergeable_trips=0
full_total_trips_due_to_ridesharing=0
total_Merged_trips_only_after_ridesharing=0



def run_main_algo(const_pass, const_delay, walk_consider, dict_trip_details):
    mergeable_trips_list[:] = []
    metadata_trips_merged.clear()
    possible_distance_merged.clear()
    ip_trips_for_algorithm.clear()
    ip_trips_for_maxMatching.clear()
    dist_dict.clear()
    list_trip_details = []
    n_of_trips = 0
    if dict_trip_details is not None:
        if dict_trip_details.get(1) is not None:
            n_of_trips += len(dict_trip_details.get(1))
            list_trip_details.extend(dict_trip_details.get(1))
        if dict_trip_details.get(2) is not None:
            n_of_trips += len(dict_trip_details.get(2))
            list_trip_details.extend(dict_trip_details.get(2))
        if dict_trip_details.get(3) is not None:
            n_of_trips += len(dict_trip_details.get(3))
            list_trip_details.extend(dict_trip_details.get(3))
        if dict_trip_details.get(4) is not None:
            n_of_trips += len(dict_trip_details.get(4))
            list_trip_details.extend(dict_trip_details.get(4))
    #print("list_trip_details:",len(list_trip_details))
    #print("NUMBER OF TRIPS",n_of_trips)
    # initialize the trip distance matrix to -1 which denotes that the trips are yet to be processed
    # trips are set to be processed only when value at [i][j] position is not -1 
    
    
    t_dist_matrix = [[-1 for x in range(n_of_trips)] for y in range(n_of_trips)]
    i = 0
    #print("Processing matrix information")
    total_distance = 0
    
    while i < len(list_trip_details):
        j = i + 1
        t1 = list_trip_details[i]
        total_distance += t1.trip_distance_from_source
        
        ip_trips_for_algorithm.add(t1.trip_id)
        while j < len(list_trip_details) :
            t2 = list_trip_details[j]
            # Trips are processed only when the two are not same and the two trips are not previously processed
            #print(t1.trip_id,t2.trip_id)
            if (t1.trip_id != t2.trip_id) and (t_dist_matrix[i][j] == -1):
                passenger_count = t1.passenger_count + t2.passenger_count
                
                if ((passenger_count <= const_pass)and (check_mergeability(t1, t2, const_delay, walk_consider))):
                    t_dist_matrix[i][j] = 1
                    t_dist_matrix[j][i] = 1
                else:
                    t_dist_matrix[i][j] = 0
                    t_dist_matrix[j][i] = 0
            else:
                t_dist_matrix[i][j] = 0
                t_dist_matrix[j][i] = 0
            j = j + 1
        metadata_trips_merged[str(t1.trip_id) + "-" + str(t1.trip_id)] = [t1]
        #total_distance += t1.trip_distance_from_source
        #total_distance += t2.trip_distance_from_source
        i = i + 1
    #print(np.matrix(t_dist_matrix))
    actual_matching(total_distance)


def actual_matching(total_distance):
    global total_number_trips_saved
    global total_savedDistance
    global total_entire_distance
    global total_unmergeable_trips
    global full_total_trips_due_to_ridesharing
    global total_Merged_trips_only_after_ridesharing
    
    graph = nx.Graph()
    #print("LLLLLLL",graph)
    graph.add_weighted_edges_from(mergeable_trips_list)
    
    #print("??????/",mergeable_trips_list)
    match_dict = dict(nx.max_weight_matching(graph, maxcardinality=True))
   # print("god",nx.max_weight_matching(graph, maxcardinality=True))
   # print("KKKK",match_dict)
    tripsSet = set()
    savedDistance = 0
    for key in match_dict:
        if (key in tripsSet) and (match_dict[key] in tripsSet):
            continue
        else:
            tripsSet.add(key)
            tripsSet.add(match_dict[key])
            keyvalue = str(key) + "-" + str(match_dict[key])
            keyvalue1 = str(match_dict[key]) + "-" + str(key)
            #print("tripsSet",tripsSet)
            #print(keyvalue1)
            if keyvalue in metadata_trips_merged.keys():
                trips = metadata_trips_merged[keyvalue]
                
                savedDistance += dist_dict[keyvalue]
            elif keyvalue1 in metadata_trips_merged.keys():
                trips = metadata_trips_merged[keyvalue1]
                
                savedDistance += dist_dict[keyvalue1]
            else :
                g=0
               
        
    no_trips_saved = len(ip_trips_for_algorithm) - len(match_dict.keys()) / 2 - len(ip_trips_for_maxMatching.difference(match_dict.keys()))
    total_number_trips_saved+=no_trips_saved
    total_savedDistance+=savedDistance
    total_entire_distance+=total_distance
    unmergeable_trips=len(ip_trips_for_algorithm) - len(ip_trips_for_maxMatching)
    total_unmergeable_trips += unmergeable_trips
    total_trips_due_to_ridesharing = len(match_dict.keys()) / 2 + len(ip_trips_for_maxMatching.difference(match_dict.keys())) + unmergeable_trips
    full_total_trips_due_to_ridesharing += total_trips_due_to_ridesharing
    total_Merged_trips_only_after_ridesharing+=(len(match_dict.keys()) / 2)
   
    
    
        
        
            
                
def check_mergeability(t1, t2, const_delay, walk_consider): 
   if walk_consider:
       # print("wit walking")
        return check_meregabilty_with_walking(t1, t2, const_delay)
   else:
       # print("without walking")
        return check_meregabilty_without_walking(t1, t2, const_delay)
   

def check_meregabilty_without_walking(t1, t2, const_delay):
   # print("@@@@@",t1.dropoff_longitude,",",t1.dropoff_lattitude,";",t2.dropoff_longitude,",",t2.dropoff_lattitude)
    url = "http://router.project-osrm.org/route/v1/driving/"+ str(t2.dropoff_longitude) + "," + str(t2.dropoff_lattitude) + ";" + str(t1.dropoff_longitude) + "," + str(t1.dropoff_lattitude)
    #print(url)
    response = urlopen(url)
    string = response.read().decode('utf-8')
    jsonObj = json.loads(string)
    if jsonObj is not None:
        duration2trips = jsonObj['routes'][0]['duration']
        distance2trips = jsonObj['routes'][0]['distance'] * float(0.000621371)
        edge1 = 0
        edge2 = 0
        distance1 = 0
        if t1.trip_duration_from_source <= t2.trip_duration_from_source:
            edge1 = t1.trip_duration_from_source
            edge2 = t2.trip_duration_from_source
            distance1 = t1.trip_distance_from_source
        else:
            edge1 = t2.trip_duration_from_source
            edge2 = t1.trip_duration_from_source
            distance1 = t2.trip_distance_from_source
        #print("edge1 edge2  duration2trips  const_delay:",edge1, edge2, duration2trips, const_delay)
        mergable_edges = merging_criteria(float(edge1), float(edge2), float(duration2trips), float(const_delay))
        
        if mergable_edges:
            ip_trips_for_maxMatching.add(t1.trip_id)
            ip_trips_for_maxMatching.add(t2.trip_id)
            edge_details = (t1.trip_id, t2.trip_id, duration2trips)
            mergeable_trips_list.append(edge_details)
            key = str(t1.trip_id) + "-" + str(t2.trip_id)
            distanceWithRidesharing = compute_distance(float(distance1), float(distance2trips))
            metadata_trips_merged[key] = [t1, t2]
            dist_dict[key] = distanceWithRidesharing  
            # print(key+"-"+str(mergable_edges))
            # print("---------------------------------------------------")
            possible_distance_merged[str(t1.trip_id) + "-" + str(t2.trip_id)] = float(edge1) + float(distance2trips)
            #print("00000",mergeable_trips_list)
    return mergable_edges
    

def check_meregabilty_with_walking(t1, t2, const_delay):
    if t1.willing_to_walk == 0 and t2.willing_to_walk == 0:
        return check_meregabilty_without_walking(t1, t2, const_delay)
    else:
        bearingAngle = 0
        urlPart1 = "http://router.project-osrm.org/nearest/v1/foot/"
        urlPart2 = "?number=40&bearingAngles="
        urlPart3 = ",180&radiuses=1342"
        tt1 = type.Rides(t1.trip_id, t1.medallion, t1.passenger_count, t1.pickup_datetime, t1.trip_duration_from_source, t1.trip_distance_from_source,
                  t1.dropoff_lattitude, t1.dropoff_longitude, t1.willing_to_walk)
        tt2 = type.Rides(t2.trip_id, t2.medallion, t2.passenger_count, t2.pickup_datetime, t2.trip_duration_from_source, t2.trip_distance_from_source,
                  t2.dropoff_lattitude, t2.dropoff_longitude, t2.willing_to_walk)
        #print(t1.trip_duration_from_source , t2.trip_duration_from_source)
            
        if t1.trip_duration_from_source <= t2.trip_duration_from_source:
            if t1.willing_to_walk == 1:
                #print("trip1")
                bearingAngle = compute_bearingAngle(float(t1.dropoff_lattitude), float(t1.dropoff_longitude), float(JFK_lat), float(JFK_long))
                bearingAngle = str(int(bearingAngle))
                # print("1", t1.dropoff_lattitude, t1.dropoff_longitude, JFK_lat, JFK_long, bearingAngle)
                
                url = urlPart1 + str(t1.dropoff_longitude)+","+ str(t1.dropoff_lattitude) + urlPart2 + bearingAngle
                url = url + urlPart3
                #print(url)
                tt1 = FindNearestDropPoint(tt1, url)
            
            if t2.willing_to_walk == 1:
                bearingAngle = compute_bearingAngle(float(tt1.dropoff_lattitude), float(tt1.dropoff_longitude), float(t2.dropoff_lattitude), float(t2.dropoff_longitude))
                bearingAngle = str(int(bearingAngle))
                # print("2", tt1.dropoff_lattitude, tt1.dropoff_longitude, t2.dropoff_lattitude, t2.dropoff_longitude, bearingAngle)
                url = urlPart1 + str(t2.dropoff_longitude) + "," + str( t2.dropoff_lattitude) + urlPart2 + bearingAngle
                url = url + urlPart3
                tt2 = FindNearestDropPoint(tt2, url)
        else:
            if t2.willing_to_walk == 1:
                bearingAngle = compute_bearingAngle(float(t2.dropoff_lattitude), float(t2.dropoff_longitude), float(JFK_lat), float(JFK_long))
                bearingAngle = str(int(bearingAngle))
                # print("3", t2.dropoff_lattitude, t2.dropoff_longitude, JFK_lat, JFK_long, bearingAngle)
                url = urlPart1 + str(t2.dropoff_longitude) + "," +str( t2.dropoff_lattitude) +urlPart2 + bearingAngle
                url = url + urlPart3
                tt2 = FindNearestDropPoint(tt2, url)
            if t1.willing_to_walk == 1:
                bearingAngle = compute_bearingAngle(float(tt2.dropoff_lattitude), float(tt2.dropoff_longitude), float(t1.dropoff_lattitude), float(t1.dropoff_longitude))
                bearingAngle = str(int(bearingAngle))
                # print("4", tt2.dropoff_lattitude, tt2.dropoff_longitude, t1.dropoff_lattitude, t1.dropoff_longitude, bearingAngle)
                url = urlPart1 + str(t1.dropoff_longitude) + "," +str( t1.dropoff_lattitude) + urlPart2 + bearingAngle
                url = url + urlPart3
                tt1 = FindNearestDropPoint(tt1, url)
        #print("final:","1:",tt1.trip_duration_from_source,"2:",tt2.trip_duration_from_source)
        url = "http://router.project-osrm.org/route/v1/driving/" + str(tt1.dropoff_longitude) + "," + str(tt1.dropoff_lattitude)+ ";" + str(tt2.dropoff_longitude) + "," + str(tt2.dropoff_lattitude)
        response = urlopen(url)
        string = response.read().decode('utf-8')
        jsonObj = json.loads(string)
        if jsonObj is not None:
            duration2trips = jsonObj['routes'][0]['duration']
            distance2trips = jsonObj['routes'][0]['distance'] * float(0.000621371)
            edge1 = 0
            edge2 = 0
            distance1 = 0
            if tt1.trip_duration_from_source <= tt2.trip_duration_from_source:
                edge1 = tt1.trip_duration_from_source
                edge2 = tt2.trip_duration_from_source
                distance1 = tt1.trip_distance_from_source
            else:
                edge1 = tt2.trip_duration_from_source
                edge2 = tt1.trip_duration_from_source
                distance1 = tt2.trip_distance_from_source
            #print("edge1,edge2,distance1,duration2trips,distance2trips:",edge1,edge2,distance1,duration2trips,distance2trips)
            mergable_edges = merging_criteria(edge1, edge2, duration2trips, const_delay)
            if mergable_edges:
                ip_trips_for_maxMatching.add(tt1.trip_id)
                ip_trips_for_maxMatching.add(tt2.trip_id)
                edge_details = (tt1.trip_id, tt2.trip_id, duration2trips)                
                mergeable_trips_list.append(edge_details)
                key = str(tt1.trip_id) + "-" + str(tt2.trip_id)
                metadata_trips_merged[key] = [tt1, tt2]
                possible_distance_merged[str(t1.trip_id) + "-" + str(t2.trip_id)] = float(edge1) + distance2trips
                distanceWithRidesharing = compute_distance(distance1, distance2trips)
                metadata_trips_merged[key] = [t1, t2]
                dist_dict[key] = distanceWithRidesharing   
    return mergable_edges
    
    
    
def compute_bearingAngle(to_lat, to_long, from_lat, from_long):
    diff_longitude = radians(from_long - to_long)
    to_lat = radians(to_lat)
    to_long = radians(to_long)
    from_lat = radians(from_lat)
    from_long = radians(from_long)
    y = cos(from_lat) * sin(diff_longitude)
    x = (cos(to_lat) * sin(from_lat)) - (sin(to_lat) * cos(from_lat) * cos(diff_longitude))
    bearingAngle = atan2(y, x)
    
    #print("@####",y,x)
    bearingAngle = degrees(bearingAngle)
    #print(bearingAngle)
    if bearingAngle < 0:
        bearingAngle = bearingAngle + 180
        
    return bearingAngle

def FindNearestDropPoint(tripData, url):
    #print(url)
    response = urlopen(url)
    string = response.read().decode('utf-8')
    jsonObj = json.loads(string)
    #print("PPPPPP",json.loads(string))
    if jsonObj is not None:
        last_point = len(jsonObj)
        #print("last_point",last_point)
        #print("imp:",str(jsonObj['waypoints'][last_point - 1]))
        drop_off_lattitude = str(jsonObj['waypoints'][last_point - 1]['location'][1])
        drop_off_longitude = str(jsonObj['waypoints'][last_point - 1]['location'][0])
        tripData.dropoff_lattitude = drop_off_lattitude
        tripData.dropoff_longitude = drop_off_longitude
        url = "http://router.project-osrm.org/route/v1/driving/" + drop_off_longitude + "," + drop_off_lattitude + ";" + JFK_long + "," + JFK_lat
        response = urlopen(url)
        string = response.read().decode('utf-8')
        jsonObj = json.loads(string)
        if jsonObj is not None:
            duration2trips = jsonObj['routes'][0]['duration']
            distance2trips = jsonObj['routes'][0]['distance'] * float(0.000621371)
            #print("duration2trips,distance2trips:",duration2trips,distance2trips)
            tripData.trip_duration_from_source = duration2trips
            tripData.trip_distance_from_source = distance2trips
    return tripData
    

def merging_criteria(edge1, edge2, inter_trip_edge, const_delay):
    increasedDuration = (((float(edge1) + float(inter_trip_edge)) - float(edge2)) / float(edge2) )
    mergable_edges_for_merging = False
    if increasedDuration <= const_delay:
        mergable_edges_for_merging = True
    return mergable_edges_for_merging

def compute_distance(distance1, distance2):
    return float(distance1) + distance2

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
    

def main():
    global total_number_trips_saved
    global number_of_pools
    conn = openConnection()
    cursor = conn.cursor()
    cursor.execute("select * from ridesharing_trips order by tpep_pickup_datetime;")
    firstRec = cursor.fetchone()
    
    startDate=firstRec[1]
     
  
    endDate = startDate + timedelta(minutes=3)
   
    the=datetime.datetime(2016, 2, 1,0,0,0)#can change the EndDate depending on the EndDate of the dataset or till which you want to run the algo
    while(endDate < the):
        
       
        query="select * from ridesharing_trips where tpep_pickup_datetime between '%s' and '%s';" % (startDate, endDate)
        
        rowsCount = cursor.execute(query)

        if rowsCount> 0:
                add_records(rowsCount)
                number_of_pools+=1
                dict_trip_details = {}
                
                for record in cursor:
                    rides = type.Rides(record[17], record[15], record[3], record[1], record[16], record[12], record[9], record[8],record[14])
                    if record[0] in dict_trip_details.keys():
                        list_of_rides_in_pool = dict_trip_details[record[0]]
                        list_of_rides_in_pool.append(rides)
                        dict_trip_details[record[0]] = list_of_rides_in_pool
                    else:
                        list_of_rides_in_pool = [rides]
                        dict_trip_details[record[0]] = list_of_rides_in_pool
               
                
                run_main_algo(3, 0.3, True, dict_trip_details)
               
                
                #pooling
                startDate = endDate + timedelta(seconds=1)
               
                endDate = startDate + timedelta(minutes=3)
                #print("End date",endDate)
                
                #print("Dates:",startDate,endDate)
                
        else:
            
            endDate=endDate + timedelta(minutes=3)
           
            #break 
            
                
                
                
        
    closeConnection(conn)
def add_records(nts):    
    global tnor
    tnor+=nts

if __name__ == "__main__":
    
    start_time = time.clock()
    main()
    print("PROCESSING TIME:",time.clock() - start_time, "seconds")
    print("total_number_trips_saved:",total_number_trips_saved)
    print("total_savedDistance:",total_savedDistance)
    print("total_entire_distance:",total_entire_distance)
    print("number_of_pools",number_of_pools)
    print("total_number_trips==>",tnor)
    print("average_trips_in_pool==>",tnor/number_of_pools)
    print("total_unmergeable_trips:",total_unmergeable_trips)
    print("full_total_trips_due_to_ridesharing",full_total_trips_due_to_ridesharing)
    print("total_Merged_trips_only_after_ridesharing",total_Merged_trips_only_after_ridesharing)

  