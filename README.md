

Pre-requisites:
------------

Before working with this algorithm, Spyder IDE and MySQL must be installed. Also the system must be connected with the internet. As we use OSRM,NetworkX APIs through the internet.

Kindly follow the below steps to run the ridesharing algorithm:

1.1.DATABSE SETUP:
-----------------------
1.Make sure the MySQL database is set up on your laptop and is working.\n
Goto the MySQL command line and do the following:
2.Create a database by name 'hi' or any name you wish to use.
  If using any name other than 'hi' for database,make sure to change in the openConnection, closeConnection functions of the db1.py,
  databaseConnector.py, type.py and algo.py python scripts.
3.Create a table ridesharing_trips before running the preprocessing code using the query : 
create table ridesharing_trips(VendorID int(11), tpep_pickup_datetime datetime,tpep_dropoff_datetime datetime,passenger_count  int(11),trip_distance_original decimal(4,2),
 pickup_longitude decimal(10,8), pickup_lattitude decimal(10,8),RatecodeID  int(11),dropoff_longitude decimal(10,8), dropoff_lattitude decimal(10,8),total_amount decimal(4,2),
 trip_time_minutes decimal(10,8),trip_distance_from_source decimal(10,2),original_average_speed  decimal(10,2), willing_to_walk int(11),medallion char(30),
  trip_duration_from_Source decimal(10,2), id int not null auto_increment, primary key(id))


1.2.PREPROCESSING
------------------------------
1.Make sure to remove all the outliers like trips with 0 passengers, null pickuptime or null dropofftime.There could any for your dataset.Just remove the outliers 
  before running the following python script files. Name your final dataset as "sample_dataset.csv", if using any other name. Make sure to change it on the line number 73 of db1.py
  Format of the dataset should be csv. Also the location of thhe dataset must be the same as db1.py.
2. Run the db1.py  after opening in Spyder IDE, to precompute the distances for the trips and  it would insert data along with their results
   on to the table ridesharing_trips.
3. This is will insert all the data after computing the distance and durationn on the table ridesharing_trips.
4.After the code has finished running, you could check the inserted data into ridesharing_trips on the MySQL database command line using the query:"select* from ridesharing_trips;"

1.3 RIDESHARING ALGORITHM
-----------------------------

1. The script files db1.py,databaseConnector.py, type.py and algo.py are all must be copied in the same folder ie same location.
2.Run the algo.py for the ridesharing algortihm to run.
3.On the python console in which the code is being run, the results like :total_number_trips_saved,total_savedDistance,number_of_pools,total_number_trips,average_trips_in_pool,total_unmergeable_trips
full_total_trips_due_to_ridesharing all would be displayed once the computation is finished. Requires to be connected to the internet for the getting the results from OSRM, networkX APIs
----------------
