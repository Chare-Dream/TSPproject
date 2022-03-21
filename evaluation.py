import pandas as pd
import numpy as np
from timeit import default_timer as timer
from math import radians, cos, sin, asin, sqrt


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth surface.
    Takes 4 numbers, containing the latitude and longitude of each point in decimal degrees.

    The default returned unit is kilometers.
    """
    # mean earth radius - https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
    avg_earth_radius = 6371.0  # 6371.0088

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))

    # calculate haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    d = sin(dlat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(dlon * 0.5) ** 2
    c = 2.0 * avg_earth_radius
    return c * asin(sqrt(d))


# Idea 3: Convert this function into a function that takes a single array of
# lat and a single vector of lon (length N) and returns a matrix N x N with all
# pairwise distances.
def haversine_np(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between paired arrays representing
    points on the earth (specified in decimal degrees)

    All args must be numpy arrays of equal length.

    Returns an array of distances for each pair of input points.
    """
    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))

    # calculate haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    d = np.sin(dlat * 0.5)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon * 0.5)**2
    c = 2.0 * 6371.0
    return c * np.arcsin(np.sqrt(d))


# Original function provided by professor which calculates the weighted trip length
def weighted_trip_length(stops_latitude, stops_longitude, weights):
    north_pole = (90, 0)
    sleigh_weight = 10
    dist = 0.0
    # Start at the North Pole with the sleigh full of gifts.
    prev_lat, prev_lon = north_pole
    prev_weight = np.sum(weights) + sleigh_weight
    for lat, lon, weight in zip(stops_latitude, stops_longitude, weights):
        # Idea 1: Calculating the distances between the points repeatedly is
        # slow. Calculate all distances once into a matrix, then use that
        # matrix here.
        dist += haversine(lat, lon, prev_lat, prev_lon) * prev_weight
        prev_lat, prev_lon = lat, lon
        prev_weight -= weight

    # Last trip back to the North Pole, with just the sleigh weight
    dist += haversine(north_pole[0], north_pole[1], prev_lat, prev_lon) * sleigh_weight

    return dist


# Original function provided by professor which calculates the WRW based on the solution provided
def weighted_reindeer_weariness(all_trips, weight_limit=1000):
    uniq_trips = all_trips.TripId.unique()

    if any(all_trips.groupby('TripId').Weight.sum() > weight_limit):
        raise Exception("One of the sleighs over weight limit!")

    dist = 0.0
    for t in uniq_trips:
        # Idea 2: There may be better/faster/simpler ways to represent a solution.
        this_trip = all_trips[all_trips.TripId == t]
        dist += weighted_trip_length(this_trip.Latitude, this_trip.Longitude, this_trip.Weight)

    return dist


# The improved function
def weighted_reindeer_weariness_new(all_trips, weight_limit=1000):
    """
    The main idea of this function is to use numpy to accelerate the speed of calculation.
    Another improvement of this function is to calculate the distances and weights of all trips at once.
    """
    # Convert the input all_trips to DataFrame in order to check if the weight of a trip exceeds the limit
    if isinstance(all_trips, pd.DataFrame):
        all_trips = pd.DataFrame(np.array(all_trips))
    else:
        all_trips = pd.DataFrame(all_trips)

    if any(all_trips.groupby(4)[3].sum() > weight_limit):
        raise Exception("One of the sleighs over weight limit!")

    # Convert the DataFrame to numpy array and use numpy.unique to
    # Get the name of each trip, the index when the trip name first appeared, and the number of gifts in each trip
    all_trips_array = np.array(all_trips)
    uniq_trips, index, counts = np.unique(all_trips_array[:, -1], return_index=True, return_counts=True)

    # Create two Latitude array to calculate the latitude difference between two adjacent gifts at once
    # First Latitude array: Insert the latitude of the North Pole at the beginning of each trip
    latitude1 = np.insert(all_trips_array[:, 1], index, 90)
    # Second Latitude array: Insert the latitude of the North Pole at the end of each trip
    latitude2 = np.append(np.insert(all_trips_array[:, 1], index[1:], 90), 90)

    # Create two Longitude array to calculate the longitude difference between two adjacent gifts at once
    # First Longitude array: Insert the longitude of the North Pole at the beginning of each trip
    longitude1 = np.insert(all_trips_array[:, 2], index, 0)
    # Second Longitude array: Insert the longitude of the North Pole at the end of each trip
    longitude2 = np.append(np.insert(all_trips_array[:, 2], index[1:], 0), 0)

    dist = haversine_np(latitude2, longitude2, latitude1, longitude1)

    # Use the cumulative sum method provided by the pandas.DataFrame.groupby for the inverse order of the weights array
    weights_array = all_trips_array[:, 3]
    weights_dataframe = pd.Series(weights_array[::-1])
    weights = np.array(weights_dataframe.groupby(weights_dataframe.index.isin(counts[::-1].cumsum()).cumsum()).cumsum())
    # Inverse the result to get the correct weight array and add the weight of the sleigh
    weights = weights[::-1] + 10
    # Insert the weight of the sleigh at the end of each trip and return the final weight array
    weights = np.append(np.insert(weights, index[1:], 10), 10)

    return np.dot(dist, weights)


start_time = timer()

gifts = pd.read_csv('gifts.csv')
sample_sub = pd.read_csv('sample_solution.csv')
all_trips = gifts.merge(sample_sub, on='GiftId')

wrw = weighted_reindeer_weariness_new(all_trips)
end_time = timer()

# It should be close to 144525525772
print("WRW = {:.0f}  (Time: {:.2f} seconds)".format(wrw, end_time - start_time))
