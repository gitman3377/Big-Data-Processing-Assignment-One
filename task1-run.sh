hdfs dfs -rm -r -f /Output/task1

hadoop jar /usr/lib/hadoop/hadoop-streaming.jar \
    -D mapreduce.job.reduces=3 \
    -files task1-mapper.py,task1-reducer.py \
    -mapper "python3 task1-mapper.py" \
    -reducer "python3 task1-reducer.py" \
    -input /Input/Trips.txt \
    -output /Output/task1