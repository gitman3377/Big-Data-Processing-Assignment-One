import sys


for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    fields = line.split(",")

    if len(fields) == 4:
        taxi_id = fields[0]
        company_id = fields[1]

        # Composite key => taxi_id + record type 0
        print(f"{taxi_id}\t0\t{company_id}")

    # Trips.txt format =>  trip_id, taxi_id, fare, distance,
    elif len(fields) == 8:
        taxi_id = fields[1]
        fare = fields[2]
        distance = fields[3]

        # Composite key => taxi_id + record type 1
        print(f"{taxi_id}\t1\t{fare}\t{distance}")
