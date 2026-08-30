import sys

trip_data = {}


for line in sys.stdin:
    line = line.strip()
    
    parts = line.split(',')
        
    try:
        taxi_id = parts[1].strip()
        fare = float(parts[2].strip())
        distance = float(parts[3].strip())
    except ValueError:
        continue
        
    if distance >= 200:
        trip_type = "long"
    elif distance >= 100:
        trip_type = "medium"
    else:
        trip_type = "short"
        
    key = f"{taxi_id},{trip_type}"
    
    if key in trip_data:
        trip_data[key][0] += 1
        trip_data[key][1] += fare
        if fare > trip_data[key][2]:
            trip_data[key][2] = fare
        if fare < trip_data[key][3]:
            trip_data[key][3] = fare
    else:
        trip_data[key] = [1, fare, fare, fare]

for key, stats in trip_data.items():
    count, sum_fare, max_fare, min_fare = stats
    print('%s\t%s\t%s\t%s\t%s' % (key, count, sum_fare, max_fare, min_fare))