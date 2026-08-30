import sys


for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    fields = line.split("\t")

    if len(fields) != 6:
        continue

    company_id = fields[0]
    total_revenue = fields[1]
    total_trips = fields[2]
    fleet_size = fields[3]
    revenue_per_taxi = fields[4]
    average_distance = fields[5]

    try:
        float(total_revenue)
    except ValueError:
        continue


    # Composite key: partition_tag + total_revenue + company_id

    # each partition by total_revenue in descending order.
    for partition_tag in ("0", "1", "2"):
        print(
            f"{partition_tag}\t"
            f"{total_revenue}\t"
            f"{company_id}\t"
            f"{total_trips}\t"
            f"{fleet_size}\t"
            f"{revenue_per_taxi}\t"
            f"{average_distance}"
        )