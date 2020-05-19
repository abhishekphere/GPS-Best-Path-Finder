"""
    This program uses a cost function to find the best path from source
    to destination using GPS data and coverts the path to kml for visualization.
"""
import os
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import math

MEANINGLESS_JUNK_THRESHOLD = 5          # Threshold for removing buggy location coordinates
TIME_THRESHOLD = 22                     # Obtained by recurrently visualizing data

def read_data():
    columns = ['Data_Type', 'time_UTC', 'A', 'Latitude', 'North_South',     # Column names considered
               'Longitude', 'East_West', 'Speed', 'Tracking_Angle']
    entries = os.listdir('FILES_TO_WORK/')                                  # Gets list of files from the directory

    all_files = []                                                          # Keeps track of all the file names
    for e in entries:
        all_files.append('FILES_TO_WORK/' + e)

    all_data_frames = []                                                    # Stores all the data frames
    for file_name in all_files:
        file = open(file_name, 'r')
        all_lines = []
        for line in file:
            # Only considers GPRMC data
            if (line.split(",")[0] == '$GPRMC'):
                # removes second sentence if two sentences present in same line
                all_lines.append(line.split(",")[:9])
        df = pd.DataFrame(all_lines, columns=columns)
        df[["time_UTC", "Latitude", "Longitude", "Speed", "Tracking_Angle"]] = \
            df[["time_UTC", "Latitude", "Longitude", "Speed", "Tracking_Angle"]].apply(pd.to_numeric)
        all_data_frames.append(df)

    # Perform data cleaning on all files
    for i in range(len(all_data_frames)):
        all_data_frames[i] = data_cleaning(all_data_frames[i])
    return all_data_frames


def data_cleaning(data_frame):
    """
    This function is responsible for data cleaning of all the data frames
    :param data_frame: data frame using pandas
    :return: cleaned data frame
    """

    # remove rows with missing values
    data_frame.dropna()

    # removes duplicate data points if the vehicle is parked
    data_frame.drop_duplicates(subset=['Latitude', 'Longitude'], keep='first', inplace=True)

    # Removes junk from the data
    removing_idx = []                                   # Keeps track of junk lines indexes

    # Used because some of the indexes are removed in previous step and it might throw invalid index error
    all_index = data_frame.index
    for idx in range(len(all_index) - 1):
        curr_longitude = data_frame['Longitude'][all_index[idx]]
        next_longitude = data_frame['Longitude'][all_index[idx+1]]
        curr_latitude = data_frame['Latitude'][all_index[idx]]
        next_latitude = data_frame['Latitude'][all_index[idx+1]]

        # To remove data with incorrect time
        time = str(data_frame['time_UTC'][all_index[idx]]).split(".")
        if(len(time[0])!=6):
            removing_idx.append(idx)
            continue

        distance = haversine(curr_longitude,curr_latitude,next_longitude,next_latitude)
        # Adds junk indexes for removal
        if (distance >= MEANINGLESS_JUNK_THRESHOLD):
            removing_idx.append(idx + 1)

    # To remove incorrect end time
    if(str(data_frame['time_UTC'][all_index[-1]]).split(".")[0]!=6):
        removing_idx.append(len(all_index)-1)
    data_frame = data_frame.drop(data_frame.index[removing_idx])

    return data_frame

def haversine(lon1,lat1,lon2,lat2):
    """
    Calculates the haversine distance between two points
    whose longitude and latitude are known
    :param lon1: longitude og point 1
    :param lat1: latitude of point 1
    :param lon2: longitude of point 2
    :param lat2: latitude of point 2
    :return: haversine distance
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    logi = lon2-lon1
    lati = lat2-lat1
    dist = 2*asin(sqrt(sin(lati/2)**2 + cos(lat1) * cos(lat2) * sin(logi/2)**2))
    dist = dist*6371

    return dist

def find_stop_signs(data_frame):
    """
    Finds all the coorinates with stop signs or signals
    :param data_frame: data of one trip
    :return: all stops signs found on this trip
    """
    stop_list = []
    for i in range(len(data_frame)):
        current_lat = data_frame.iloc[i]['Latitude']
        current_lon = data_frame.iloc[i]['Longitude']
        current_speed = data_frame.iloc[i]['Speed']

        #Check if the speed is lower than 1 knot
        if (current_speed < 1.0):
            # To avoid having multiple stop signs for the same location
            if(len(stop_list)>0):
                dist_with_prev_stop = haversine(current_lon, current_lat, stop_list[-1][0],stop_list[-1][1])
                if (dist_with_prev_stop <= 10):
                    stop_list.pop()
            stop_list.append((current_lon, current_lat))
    return stop_list

def find_left_turns(data_frame):
    """
    Finds all coordiantes where left turn was taken
    :param data_frame: data of one trip
    :return: list of all left turns for given trip
    """
    left_turns = []
    speed = data_frame.iloc[0]['Speed']
    angle = data_frame.iloc[0]['Tracking_Angle']
    for i in range(data_frame.shape[0]):
        speed_cur = data_frame.iloc[i]['Speed']
        if speed_cur < speed and speed_cur < 10:
            continue
        else:
            diff_angle = data_frame.iloc[i]['Tracking_Angle'] - angle
            if diff_angle >= 25:
                left_turns.append((data_frame.iloc[i]['Longitude'], data_frame.iloc[i]['Latitude']))
        speed = speed_cur
        angle = data_frame.iloc[i]['Tracking_Angle']

    return left_turns

def find_time_taken(data_frame):
    """
    Calculates the time taken from start of the trip to end
    :param data_frame: data of one trip
    :return: time taken
    """
    start_time = str(data_frame.iloc[0]['time_UTC'])
    end_time = str(data_frame.iloc[-1]['time_UTC'])
    total_time = getTime(end_time) - getTime(start_time)
    total_time = (total_time / 60)
    return total_time

def getTime(time):
    """
    This function converts the time into seconds.
    :param time: time
    :return: time in secs
    """
    hours = int(time[:2])
    mins = int(time[2:4])
    secs = int(time[4:6])
    time = (hours * 60 * 60) + (mins * 60) + (secs)

    return time

def findBestRoute(data):
    """
    Finds the best route based on the cost function
    :param data: entire data
    :return: best cost function, best route
    """
    # dict = {}
    # ind = 0
    min_cost_function = math.inf
    best_route = None
    for d in data:
        time_taken = abs(find_time_taken(d))
        stop_signs = find_stop_signs(d)
        left_turns = find_left_turns(d)
        cost_function = 0.7*time_taken + 0.2*len(left_turns) + 0.1*len(stop_signs)

        if(cost_function<min_cost_function and find_time_taken(d) > TIME_THRESHOLD):
            min_cost_function = cost_function
            best_route = d

    return min_cost_function,best_route


def add_header(kml_file):
    """
    Adds header to the kml file.
    :param kml_file: kml file
    :return: updated kml file
    """
    kml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml_file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml_file.write("<Document>\n")
    kml_file.write('<Style id="yellowPoly">\n')
    kml_file.write("<LineStyle>\n")
    kml_file.write("<color>Af00ffff</color>\n")
    kml_file.write("<width>6</width>\n")
    kml_file.write("</LineStyle>\n")
    kml_file.write("<PolyStyle>\n")
    kml_file.write("<color>7f00ff00</color>\n")
    kml_file.write("</PolyStyle>\n")
    kml_file.write("</Style>\n")
    kml_file.write("<Placemark><styleUrl>#yellowPoly</styleUrl>\n")
    kml_file.write("<LineString>\n")
    kml_file.write("<Description>Speed in MPH, not altitude.</Description>\n")
    kml_file.write("<extrude>1</extrude>\n")
    kml_file.write("<tesselate>1</tesselate>\n")
    kml_file.write("<altitudeMode>absolute</altitudeMode>\n")
    kml_file.write("<coordinates>\n")

def convert_to_mins(coordinate):
    """
    Converts coordinates in mins format.
    :param coordinate: Latitude or Longitude
    :return: Latitude or Longitude in mins
    """
    number = float(coordinate)
    dist = (int(number / 100)) + (number - (int(number / 100) * 100)) / 60
    return str(dist)


def add_coordinates_to_body(kml_file, data_frame):
    """
    Adds coordinates to the body.
    :param kml_file: kml file
    :param data_frame: data frame with the coordinates
    :return: updated kml file
    """
    for row in data_frame.iterrows():
        if not (math.isnan(list(row[1])[3]) or math.isnan(list(row[1])[5])):
            latitude = convert_to_mins((list(row[1]))[3])
            longitude = convert_to_mins((list(row[1]))[5])
            kml_file.write('-' + longitude+ ',' + latitude + ',' + str(0) + '\n')

def add_red_placemark_for_stops(list_of_stops, kml_file):
    """
    Adds red pins where stop was taken.
    :param list_of_stops: list of stops
    :param kml_file: kml file
    :return: updated kml file
    """
    for longitude, latitude in list_of_stops:
        longitude = convert_to_mins(longitude)
        latitude = convert_to_mins(latitude)
        kml_file.write("<Placemark>\n")
        kml_file.write("<description>Red PIN for A Stop</description>\n")
        kml_file.write('<Style id="normalPlacemark">\n')
        kml_file.write("<IconStyle>\n")
        kml_file.write("<color>ff0000ff</color>\n")
        kml_file.write("<Icon>\n")
        kml_file.write("<href>http://maps.google.com/mapfiles/kml/paddle/1.png</href>\n")
        kml_file.write("</Icon>\n")
        kml_file.write("</IconStyle>\n")
        kml_file.write("</Style>\n")
        kml_file.write("<Point>\n")
        kml_file.write('<coordinates>-' + longitude + ',' + latitude + ',0</coordinates>\n')
        kml_file.write("</Point>\n")
        kml_file.write("</Placemark>\n")

def add_red_placemark_for_left_turns(list_of_left_turns, kml_file):
    """
    Adds green pins where stop was taken.
    :param list_of_left_turns: list of left turns
    :param kml_file: kml file
    :return: updated kml file
    """
    for longitude, latitude in list_of_left_turns:
        longitude = convert_to_mins(longitude)
        latitude = convert_to_mins(latitude)
        kml_file.write("<Placemark>\n")
        kml_file.write("<description>Green PIN for A Left Turn</description>\n")
        kml_file.write('<Style id="normalPlacemark">\n')
        kml_file.write("<IconStyle>\n")
        kml_file.write("<color>ff00ffff</color>\n")
        kml_file.write("<Icon>\n")
        kml_file.write("<href>http://maps.google.com/mapfiles/ms/icons/green-dot.png</href>\n")
        kml_file.write("</Icon>\n")
        kml_file.write("</IconStyle>\n")
        kml_file.write("</Style>\n")
        kml_file.write("<Point>\n")
        kml_file.write('<coordinates>-' + longitude + ',' + latitude + ',0</coordinates>\n')
        kml_file.write("</Point>\n")
        kml_file.write("</Placemark>\n")

def add_body(kml_file, data_frame, list_of_stops, list_of_left_turns):
    """
    Adds body to kml file.
    :param kml_file: kml file
    :param data_frame: data frame with coordinates
    :param list_of_stops: list_of_stops
    :param list_of_left_turns: list_of_left_turns
    :return: updated kml file
    """
    add_coordinates_to_body(kml_file, data_frame)

    # Tags after adding coordinates
    kml_file.write("</coordinates>\n")
    kml_file.write("</LineString>\n")
    kml_file.write("</Placemark>\n")

    # Adds red placemarks where vehicle was stopped
    add_red_placemark_for_stops(list_of_stops, kml_file)

    # Adds green placemarks where vehicle took a left turn
    add_red_placemark_for_left_turns(list_of_left_turns, kml_file)

def add_trailer(kml_file):
    """
    Adds trailer to kml file.
    :param kml_file: kml file
    :return: updated kml file
    """
    kml_file.write("</Document>\n")
    kml_file.write("</kml>\n")


def convert_GPS_to_KML(data_frame, list_of_stops, list_of_left_turns):
    """
    Converts gps data file to kml file for visualization.
    :param data_frame: data frame of the best route found
    :param list_of_stops: list_of_stops of the best route
    :param list_of_left_turns: list_of_left_turns of the best route
    :return: created kml file
    """
    kml_file = open('kml_file.kml', 'w')
    add_header(kml_file)
    add_body(kml_file, data_frame,list_of_stops,list_of_left_turns)
    add_trailer(kml_file)


data = read_data()
min_cost_function,best_route = findBestRoute(data)
# Prints the required information
print("Min Cost function = ",min_cost_function)
print("min time = ",find_time_taken(best_route))
print("Min left turns = ",find_left_turns(best_route))
print("Min stop signs = ",find_stop_signs(best_route))
convert_GPS_to_KML(best_route,find_stop_signs(best_route), find_left_turns(best_route))





