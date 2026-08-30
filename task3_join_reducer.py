import sys


current_taxi = None
current_company = None


for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    fields = line.split("\t")

    taxi_id = fields[0]
    record_type = fields[1]

    if taxi_id != current_taxi:
        current_taxi = taxi_id
        current_company = None

    # Record type 0 = taxi information.
    # Format: taxi_id, 0, company_id
    if record_type == "0":
        if len(fields) >= 3:
            current_company = fields[2]

    # Record type 1 = trip information.
    # Format: taxi_id, 1, fare, distance
    elif record_type == "1":
        if len(fields) >= 4 and current_company is not None:
            fare = fields[2]
            distance = fields[3]

            print(
                f"{current_company}\t"
                f"{taxi_id}\t"
                f"{fare}\t"
                f"{distance}"
            )