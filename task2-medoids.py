#!/usr/bin/env python3
# Task 2 Helper
#
# It does not touch the data set at all. It only looks at the few result lines
# the reducers produced for one iteration (one line per cluster) and:
#   1. prints the iteration report asked for in the specification
#   2. writes the medoids the next iteration should use
#   3. writes 1 or 0 into converged.txt so task2-run.sh knows when to stop

import sys

MEDOIDS_FILE = "medoids.txt"                # medoids this iteration used
JOB_OUTPUT_FILE = "iteration_output.txt"    # what the reducers just produced
NEXT_MEDOIDS_FILE = "medoids.next"          # medoids for the next iteration
CONVERGED_FILE = "converged.txt"            # 1 = stop, 0 = keep going


# Read the medoids file The values are kept as text because we only print
# them and compare them, we never do maths with them here
def get_medoids(filepath):
    medoids = []
    with open(filepath) as handle:
        for line in handle:
            line = line.strip()
            if line:
                x, y = line.split("\t")
                medoids.append((x, y))
    return medoids


# Read the reducer output of this iteration
# Returns a dictionary so we can look a cluster up by its number
def get_job_output(filepath, cluster_count):
    results = {}
    with open(filepath) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue                    # skip blank lines
            fields = line.split("\t")
            if len(fields) != 5:
                continue                    # skip anything unexpected
            cluster = int(fields[0])
            if 0 <= cluster < cluster_count:
                results[cluster] = (fields[1], fields[2], fields[3], fields[4])
    return results



# The iteration number is passed in by task2-run.sh, only for printing
if len(sys.argv) != 2:
    sys.stderr.write("Usage: task2-medoids.py <iteration_number>\n")
    sys.exit(1)
iteration = sys.argv[1]

medoids = get_medoids(MEDOIDS_FILE)
results = get_job_output(JOB_OUTPUT_FILE, len(medoids))

# Print the report for this iteration
print("")
print("===== Iteration %s =====" % iteration)
print("medoid_x\tmedoid_y\t#points\tavg_dissimilarity")

next_medoids = []
changed = 0                                 # becomes 1 if any medoid moves

for cluster in range(len(medoids)):
    medoid_x, medoid_y = medoids[cluster]

    if cluster not in results:
        # No points went to this cluster, so there is no reducer line for it
        # Keep its old medoid so we always still have k medoids
        print("%s\t%s\t0\t0.00" % (medoid_x, medoid_y))
        next_medoids.append((medoid_x, medoid_y))
        continue

    new_x, new_y, points, avg_dissimilarity = results[cluster]
    # The medoid printed is the one the points were given to in this
    # iteration, so the numbers on the line belong to it
    print("%s\t%s\t%s\t%s" % (medoid_x, medoid_y, points, avg_dissimilarity))
    next_medoids.append((new_x, new_y))
    # Compared as numbers so that "10" and "10.0" do not look like a move
    if float(new_x) != float(medoid_x) or float(new_y) != float(medoid_y):
        changed = 1

# Save the medoids for the next iteration
with open(NEXT_MEDOIDS_FILE, "w") as handle:
    for x, y in next_medoids:
        handle.write("%s\t%s\n" % (x, y))

# If nothing moved, no point can change cluster either, so we have converged
with open(CONVERGED_FILE, "w") as handle:
    handle.write("0\n" if changed else "1\n")

