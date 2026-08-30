import sys


records = []
partition_tag = None


for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    fields = line.split("\t")

    if len(fields) != 7:
        continue

    partition_tag = fields[0]

    total_revenue = fields[1]
    company_id = fields[2]
    total_trips = fields[3]
    fleet_size = fields[4]
    revenue_per_taxi = fields[5]
    average_distance = fields[6]

    records.append(
        (
            company_id,
            total_revenue,
            total_trips,
            fleet_size,
            revenue_per_taxi,
            average_distance,
        )
    )



if partition_tag is not None and records:

    segment_for_tag = {
        "0": 0,
        "1": 1,
        "2": 2,
    }

    segment_number = segment_for_tag[partition_tag]
    total_companies = len(records)

    base_size = total_companies // 3
    remainder = total_companies % 3

    sizes = [
        base_size + (1 if i < remainder else 0)
        for i in range(3)
    ]

    start = sum(sizes[:segment_number])
    end = start + sizes[segment_number]

    for record in records[start:end]:
        (
            company_id,
            total_revenue,
            total_trips,
            fleet_size,
            revenue_per_taxi,
            average_distance,
        ) = record

        print(
            f"{company_id}\t"
            f"{float(total_revenue):.2f}\t"
            f"{int(total_trips)}\t"
            f"{int(fleet_size)}\t"
            f"{float(revenue_per_taxi):.2f}\t"
            f"{float(average_distance):.2f}"
        )
