#!/usr/bin/env python3
# Task 2 Reducer
# All the points of one cluster arrive here together The reducer counts them,
# works out the average distance to the current medoid, and then tries every 
# point as a possible new medoid, keeping whichever one is cheapest
# It is started in one of two modes:
#   iterate: used during the loop, prints the new medoid of each cluster
#   final: used for the last job, prints the finished answer

import sys
from math import sqrt

# Sent to every machine with -files, same as in the mapper
MEDOIDS_FILE = "medoids.txt"

# Tell Hadoop we are still working after this many candidates, so a slow job
# is not killed for looking frozen
PROGRESS_EVERY = 1000


# Read the medoids file into a list like [[x, y], [x, y], ...]
def get_medoids(filepath):
    medoids = []
    with open(filepath) as handle:
        for line in handle:
            line = line.strip()
            if line:
                x, y = line.split("\t")
                medoids.append([float(x), float(y)])
    return medoids


# Send a still alive message to Hadoop
def report_progress(message):
    sys.stderr.write("reporter:status:%s\n" % message)
    sys.stderr.flush()


# Try every point of the cluster as the new medoid and return the best one
# The cost of a point is the average distance from it to all the other points in the cluster, and the point with the lowest cost wins
def best_swap(points, total_weight):
    # Sorting first means the answer never depends on the order the points happened to arrive in
    points.sort()
    best_x, best_y, best_cost = points[0][0], points[0][1], None

    for i in range(len(points)):
        # this is the point we are testing as a new medoid
        candidate_x, candidate_y = points[i][0], points[i][1]
        total = 0.0
        for j in range(len(points)):
            # distance from the candidate to every other point, multiplied by
            # how many trips ended at that other point
            dx = points[j][0] - candidate_x
            dy = points[j][1] - candidate_y
            total += points[j][2] * sqrt(dx * dx + dy * dy)
        cost = total / total_weight         # average distance = the cost
        # Keep it only if it is strictly cheaper, so ties keep the first one
        if best_cost is None or cost < best_cost:
            best_x, best_y, best_cost = candidate_x, candidate_y, cost
        if (i + 1) % PROGRESS_EVERY == 0:
            report_progress("swap evaluation %d/%d" % (i + 1, len(points)))

    return best_x, best_y


# Print the one result line for a cluster
def emit(cluster, points, total_weight, total_distance, medoids, final):
    # average distance from the points to the medoid they were assigned to
    avg_dissimilarity = total_distance / total_weight if total_weight else 0.0

    if final:
        # The medoids have stopped moving, so just report this medoid and its
        # numbers. No swapping is needed here
        print("%r\t%r\t%d\t%.2f" % (
            medoids[cluster][0], medoids[cluster][1],
            total_weight, avg_dissimilarity))
    else:
        # Still looping, so find the new medoid and report it as well
        new_x, new_y = best_swap(points, total_weight)
        print("%d\t%r\t%r\t%d\t%.2f" % (
            cluster, new_x, new_y, total_weight, avg_dissimilarity))


# Read the mapper output and deal with one cluster at a time
def update_medoids(medoids, final):
    current = None                          # cluster we are working on now
    points = []                             # its points, as [x, y, weight]
    total_weight = 0                        # how many trips in the cluster
    total_distance = 0.0                    # their total distance to the medoid

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue                        # skip blank lines

        fields = line.split("\t")
        if len(fields) != 5:
            continue                        # skip anything unexpected
        try:
            cluster = int(fields[0])
            x = float(fields[1])
            y = float(fields[2])
            weight = int(fields[3])
            distance = float(fields[4])
        except ValueError:
            continue                        # skip lines that are not numbers

        # This works because Hadoop sorts the map output by key before it is
        # passed to the reducer, so one cluster arrives as a contiguous run
        if cluster != current:
            if current is not None:     # the previous cluster is complete
                emit(current, points, total_weight, total_distance, medoids, final)
            # start collecting the new cluster from scratch
            current = cluster
            points = []
            total_weight = 0
            total_distance = 0.0

        # add this record into the totals for the current cluster
        total_weight += weight
        total_distance += distance
        if not final:                   # candidates are only needed for a swap
            points.append([x, y, weight])

    if current is not None:             # last cluster handled by this reducer
        emit(current, points, total_weight, total_distance, medoids, final)



# The mode (iterate or final) is passed in by task2-run.sh
if len(sys.argv) < 2 or sys.argv[1] not in ("iterate", "final"):
    sys.stderr.write("Usage: task2-reducer.py <iterate|final>\n")
    sys.exit(1)
update_medoids(get_medoids(MEDOIDS_FILE), sys.argv[1] == "final")
