from math import sin, cos, sqrt, atan2, radians, asin
import math
from datetime import datetime
from datetime import timedelta
import numpy as np
import pygrib
import os
def decode_flight(origin, destination, route):
    import requests
    def return_AEROdata(method_name, **kwargs):
        username = 'USMCman'
        auth_key = 'acb3d27ce80ea60c5ac2305a2df9364c8be2c255'
        origin_url = 'https://flightxml.flightaware.com/json/FlightXML2/' + method_name
        kwargs=kwargs['kwargs']
        origin_loc = requests.get(origin_url, params=kwargs, auth=(username, auth_key))
        data_json = origin_loc.json()
        return data_json
    json_data = return_AEROdata('DecodeRoute', kwargs={'origin':origin,'route':route,'destination':destination})
    if list(json_data.keys())[0] == 'error':
        response = print('Ensure route string is formatted with spaces between fixes (no commas or other delimiters)')
    elif list(json_data.keys())[0] != 'error':
        def decode_route_result(return_json):
            new_route_dict = {}
            route_dict = return_json['DecodeRouteResult']['data']
            wp_names, wp_type, latitudes, longitudes = [], [], [], []
            for waypoints in route_dict:
                name = waypoints['name']
                waypoint_type = waypoints['type']
                waypoint_latitude = waypoints['latitude']
                waypoint_longitude = waypoints['longitude']
                wp_names.append(name)
                wp_type.append(waypoint_type)
                latitudes.append(waypoint_latitude)
                longitudes.append(waypoint_longitude)
            new_route_dict = {
                'names':wp_names,
                'types':wp_type,
                'lats':latitudes,
                'lons':longitudes
            }
            return new_route_dict
        response = decode_route_result(json_data)
    return response
def find_lengthattrs(fix_list, time_delta):
    length_list = [0,distance_between_points(fix_list[0], fix_list[1])]
    duration_list = [0,]
    total_time = time_delta
    length_dict = {}
    for index, fixes in enumerate(fix_list[2:]):
        if index == 0:
            leg_dist = distance_between_points(fix_list[1], fixes)
            length_list.append(leg_dist)
        elif index == len(fix_list) - 3:
            leg_dist = distance_between_points(fix_list[-2], fixes)
            length_list.append(leg_dist)
        else:
            leg_dist = distance_between_points(fix_list[index+1], fixes)
            length_list.append(leg_dist)
    length_dict['length_list']=length_list
    length_dict['total_length'] = sum(length_list)
    average_speed = sum(length_list)/((total_time.total_seconds())/3600)
    duration_list = [timedelta(hours=(distance/average_speed)) for distance in length_list]
    length_dict['duration_list'] = duration_list
    return length_dict
def find_filename(point_time, time_list):
    td = [abs(file_time - point_time).total_seconds() for file_time in time_list][0]
    search = point_time + timedelta(seconds=td)
    try:
        search_index = time_list.index(search)
    except:
        search = point_time - timedelta(seconds=td)
        search_index = time_list.index(search)
    return search_index
def distance_between_points(point1, point2):
    lon1, lat1, lon2, lat2 = point1[0], point1[1], point2[0], point2[1]
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956
    return round(c * r, 1)
def meters_convert(number,unit):
    if unit == 'feet':
        num = int(round(number/3.28084, 0))
    elif unit == 'meters':
        num = int(round((int(number) * 3.28084), 0))
    else:
        print("Function needs units!")
    return num
def get_value(file_name, sample_point, altitude, coord_range):
    file_path = '/home/howsTheRides/howsTheRides/polls/separated_bins/' + file_name
    grbs = pygrib.open(file_path)
    data_dict = {}
    meters_frmalt = meters_convert(altitude, "feet")
    indicies = []
    lat_min, lat_max = (sample_point[1] - 0.1), (sample_point[1] + 0.1)
    for grb in grbs:
        if meters_frmalt == grb.level:
            data = grb.data()
            # data is 3x - 1 dimensional arrays:
            def closest_node(node, nodes):
                #nodes = np.asarray(nodes)
                dist = nodes - node
                return np.argmin(abs(dist))
            data_dict['values']=data[0]
            data_dict['lats']=data[1]
            data_dict['lons'] = data[2]
            closest_lon = closest_node(sample_point[0], data_dict['lons'])
            closest_lat = closest_node(sample_point[1], data_dict['lats'])
            closest_lat, closest_lon = data_dict['lats'].flatten()[closest_lat], data_dict['lons'].flatten()[closest_lon]
            lat_index, lon_index = np.where(data_dict['lats'] == closest_lat), np.where(data_dict['lons'] == closest_lon)
            closest_value = data_dict['values'][lat_index[0],lon_index[1]]
            return closest_value
def get_turbvalues(departure_time, arrival_time, lonlat_list):
    bin_file_directory = "/home/howsTheRides/howsTheRides/polls/separated_bins/"
    files = sorted([file if file.endswith(".bin") else file for file in os.listdir(bin_file_directory)])
    file_times = [datetime.strptime(file.strip('.bin'),'%Y-%m-%d %H:%M:%S') for file in files]
    readable_filetimes = [str(file) for file in file_times]
    query_filelist = []
    now = datetime.utcnow()
    flight_time = arrival_time - departure_time
    lat_min = min([point[1] for point in lonlat_list])
    lat_max = max([point[1] for point in lonlat_list])
    lon_min = min([point[0] for point in lonlat_list])
    lon_max = max([point[0] for point in lonlat_list])
    coord_range = lat_min, lat_max, lon_min, lon_max
    turb_list = []
    for index, each_point in enumerate(lonlat_list):
        if index == 0:
            file_name = files[find_filename(departure_time, file_times)]
            fix_time = departure_time
        elif index == len(lonlat_list) - 1:
            file_name = files[find_filename(arrival_time, file_times)]
            fix_time = departure_time
        else:
            total_duration = [x.total_seconds() for x in find_lengthattrs(lonlat_list, flight_time)['duration_list'][:index + 1]]
            fix_time = departure_time + timedelta(minutes=(sum(total_duration)/60))
            file_name = files[find_filename(fix_time, file_times)]
        wp_turb_value = get_value(file_name, each_point, 38000, coord_range)
        turb_list.append(wp_turb_value[0])
    return turb_list
