import sys


current_company = None
current_taxi = None

fare_sum = 0.0
trip_count = 0
distance_sum = 0.0


def emit_result():
    if current_company is not None and current_taxi is not None:
        print(
            f"{current_company}\t"
            f"{current_taxi}\t"
            f"{fare_sum}\t"
            f"{trip_count}\t"
            f"{distance_sum}"
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

    if (
        company_id == current_company
        and taxi_id == current_taxi
    ):
        fare_sum += fare
        trip_count += count
        distance_sum += distance

    else:
        emit_result()

        current_company = company_id
        current_taxi = taxi_id

        fare_sum = fare
        trip_count = count
        distance_sum = distance


emit_result()