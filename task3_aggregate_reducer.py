import sys


current_company = None
current_taxi = None

total_revenue = 0.0
total_trips = 0
fleet_size = 0
total_distance = 0.0


def emit_company():
    if current_company is None:
        return

    if fleet_size == 0 or total_trips == 0:
        return

    revenue_per_taxi = total_revenue / fleet_size
    average_distance = total_distance / total_trips

    print(
        f"{current_company}\t"
        f"{total_revenue:.2f}\t"
        f"{total_trips}\t"
        f"{fleet_size}\t"
        f"{revenue_per_taxi:.2f}\t"
        f"{average_distance:.2f}"
    )


for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    fields = line.split("\t")

    if len(fields) != 5:
        continue

    company_id = fields[0]
    taxi_id = fields[1]

    try:
        fare = float(fields[2])
        count = int(fields[3])
        distance = float(fields[4])
    except ValueError:
        continue

    # New company
    if company_id != current_company:

        emit_company()

        current_company = company_id
        current_taxi = None

        total_revenue = 0.0
        total_trips = 0
        fleet_size = 0
        total_distance = 0.0

    # New distinct taxi within this company
    if taxi_id != current_taxi:
        fleet_size += 1
        current_taxi = taxi_id

    total_revenue += fare
    total_trips += count
    total_distance += distance


emit_company()