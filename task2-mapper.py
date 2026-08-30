#!/usr/bin/env python3
# Task 2 Mapper
# Each mapper reads part of Trips.txt, one line at a time For every trip it
# takes the drop-off point (x, y), works out which medoid is closest, and
# reports that point as belonging to that medoid's cluster
import sys
from math import sqrt

# The current medoids are sent to every machine with the files option, so the
# file sits next to the script and can be opened by name
MEDOIDS_FILE = "medoids.txt"

# Safety limit If we are ever holding this many different points in memory we
# print them out and start again, so the mapper cannot run out of memory
MAX_STATE_ENTRIES = 200000

# We store three things about every point, these are just the slot numbers
CLUSTER, WEIGHT, DISTANCE = 0, 1, 2


# Read the medoids file into a list like [[x, y], [x, y], ...]
def get_medoids(filepath):
    medoids = []
    with open(filepath) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue                    # skip blank lines
            x, y = line.split("\t")
            medoids.append([float(x), float(y)])
    if not medoids:
        # No medoids means the job was set up wrongly, so stop with an error
        sys.stderr.write("ERROR: no medoids found in %s\n" % filepath)
        sys.exit(1)
    return medoids


# Find which medoid is nearest to the point (x, y)
# Returns its position in the list and how far away it is
def closest_medoid(x, y, medoids):
    best_index = 0
    best_distance = None
    for index in range(len(medoids)):
        # straight-line (Euclidean) distance between the point and this medoid
        dx = x - medoids[index][0]
        dy = y - medoids[index][1]
        distance = sqrt(dx * dx + dy * dy)
        # Keep it only if it is strictly closer. If two medoids are the same
        # distance away the first one wins, so the result is always the same
        if best_distance is None or distance < best_distance:
            best_index = index
            best_distance = distance
    return best_index, best_distance


# Print everything we have collected so far, then empty the memory
def flush(state):
    for (x, y), agg in state.items():
        weight = agg[WEIGHT]
        # weight        = how many trips finished at this exact point
        # weight * dist = the total distance of those trips to their medoid,
        #                 so the reducer only has to add numbers up
        print("%d\t%r\t%r\t%d\t%r" % (
            agg[CLUSTER], x, y, weight, weight * agg[DISTANCE]))
    state.clear()


# Read the trips and group them by drop-off point
def create_clusters(medoids):
    # This is the "in-mapper combining" memory. It is kept between input lines
    # and holds one entry per different drop-off point, not one per trip
    # Key is the point (x, y), value is [cluster, how many trips, distance]
    state = {}

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue                        # skip blank lines

        cord = line.split(",")
        if len(cord) != 8:
            continue                        # skip broken lines
        try:
            x = float(cord[6])              # drop-off x is the 7th field
            y = float(cord[7])              # drop-off y is the 8th field
        except ValueError:
            continue                        # skip lines that are not numbers

        agg = state.get((x, y))
        if agg is None:
            # First time we see this point, so work out its cluster once
            cluster, distance = closest_medoid(x, y, medoids)
            state[(x, y)] = [cluster, 1, distance]
            if len(state) >= MAX_STATE_ENTRIES:
                flush(state)                # memory is getting full, emptying it
        else:
            # We have seen this exact point before, so just count it again
            # This saves repeating the distance calculation for every trip
            agg[WEIGHT] += 1
    # We have read the whole split, so send out what is left in memory
    flush(state)



# Load the medoids, then start reading the trips
create_clusters(get_medoids(MEDOIDS_FILE))
