import sys

current_taxi_id = None
current_trip_type = None
current_count = 0
current_sum_fare = 0.0
current_max_fare = -1.0
current_min_fare = float('inf')

taxi_id = None
trip_type = None


for line in sys.stdin:
    line = line.strip()
    
    try:
        composite_key, count_str, sum_str, max_str, min_str = line.split('\t')
        taxi_id, trip_type = composite_key.split(',')
        count = int(count_str)
        sum_fare = float(sum_str)
        max_fare = float(max_str)
        min_fare = float(min_str)
    except ValueError:
        continue
        
    if current_taxi_id == taxi_id and current_trip_type == trip_type:
        current_count += count
        current_sum_fare += sum_fare
        if max_fare > current_max_fare:
            current_max_fare = max_fare
        if min_fare < current_min_fare:
            current_min_fare = min_fare
    else:
        if current_taxi_id:
            avg_fare = current_sum_fare / current_count
            print('%s\t%s\t%s\t%.2f\t%.2f\t%.2f' % (current_taxi_id, current_trip_type, current_count, current_max_fare, current_min_fare, avg_fare))
            
        current_count = count
        current_sum_fare = sum_fare
        current_max_fare = max_fare
        current_min_fare = min_fare
        current_taxi_id = taxi_id
        current_trip_type = trip_type

if current_taxi_id == taxi_id and current_trip_type == trip_type:
    avg_fare = current_sum_fare / current_count
    print('%s\t%s\t%s\t%.2f\t%.2f\t%.2f' % (current_taxi_id, current_trip_type, current_count, current_max_fare, current_min_fare, avg_fare))