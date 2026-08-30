import sys


for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    fields = line.split("\t")

    if len(fields) != 4:
        continue

    company_id = fields[0]
    taxi_id = fields[1]
    fare = fields[2]
    distance = fields[3]

    # Composite key: company_id + taxi_id
    # Value: fare + trip count + distance
    print(
        f"{company_id}\t"
        f"{taxi_id}\t"
        f"{fare}\t"
        f"1\t"
        f"{distance}"
    )