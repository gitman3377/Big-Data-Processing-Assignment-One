#!/bin/bash

# ============================================================
# Task 3 - Company Performance Analysis
#
# Job 1: Join Trips.txt with Taxis.txt
# Job 2: Aggregate company performance statistics
# Job 3: Sort companies by total revenue in descending order
# ============================================================

STREAMING_JAR="/usr/lib/hadoop/hadoop-streaming.jar"

JOIN_OUTPUT="/tmp/task3_join"
AGG_OUTPUT="/tmp/task3_aggregate"
FINAL_OUTPUT="/Output/task3"


# ------------------------------------------------------------
# Clean previous outputs
# ------------------------------------------------------------

hadoop fs -rm -r -f "$JOIN_OUTPUT"
hadoop fs -rm -r -f "$AGG_OUTPUT"
hadoop fs -rm -r -f "$FINAL_OUTPUT"

#!/bin/bash

# ============================================================
# Task 3 - Company Performance Analysis
#
# Job 1: Join Trips.txt with Taxis.txt
# Job 2: Aggregate company performance statistics
# Job 3: Sort companies by total revenue in descending order
# ============================================================

STREAMING_JAR="/usr/lib/hadoop/hadoop-streaming.jar"

JOIN_OUTPUT="/tmp/task3_join"
AGG_OUTPUT="/tmp/task3_aggregate"
FINAL_OUTPUT="/Output/task3"


# ------------------------------------------------------------
# Clean previous outputs
# ------------------------------------------------------------

hadoop fs -rm -r -f "$JOIN_OUTPUT"
hadoop fs -rm -r -f "$AGG_OUTPUT"
hadoop fs -rm -r -f "$FINAL_OUTPUT"


# ============================================================
# JOB 1 - JOIN
# ============================================================

echo "Running Task 3 - Job 1: Join"

hadoop jar "$STREAMING_JAR" \
    -D stream.num.map.output.key.fields=2 \
    -D mapred.text.key.partitioner.options=-k1,1 \
    -D mapreduce.job.reduces=3 \
    -files task3_join_mapper.py,task3_join_reducer.py \
    -mapper "python3 task3_join_mapper.py" \
    -reducer "python3 task3_join_reducer.py" \
    -input /Input/Trips.txt \
    -input /Input/Taxis.txt \
    -output "$JOIN_OUTPUT" \
    -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner

if [ $? -ne 0 ]; then
    echo "Job 1 failed."
    exit 1
fi

echo "Job 1 completed."


# ============================================================
# JOB 2 - AGGREGATION
# ============================================================

echo "Running Task 3 - Job 2: Aggregation"

hadoop jar "$STREAMING_JAR" \
    -D stream.num.map.output.key.fields=2 \
    -D stream.num.reduce.output.key.fields=2 \
    -D mapred.text.key.partitioner.options=-k1,1 \
    -D mapreduce.job.reduces=3 \
    -files task3_aggregate_mapper.py,task3_aggregate_combiner.py,task3_aggregate_reducer.py \
    -mapper "python3 task3_aggregate_mapper.py" \
    -combiner "python3 task3_aggregate_combiner.py" \
    -reducer "python3 task3_aggregate_reducer.py" \
    -input "$JOIN_OUTPUT" \
    -output "$AGG_OUTPUT" \
    -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner

if [ $? -ne 0 ]; then
    echo "Job 2 failed."
    exit 1
fi

echo "Job 2 completed."


# ============================================================
# JOB 3 - SORT
# ============================================================

echo "Running Task 3 - Job 3: Sorting"

hadoop jar "$STREAMING_JAR" \
    -D stream.num.map.output.key.fields=3 \
    -D mapred.text.key.partitioner.options=-k1,1 \
    -D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \
    -D mapred.text.key.comparator.options="-k1,1n -k2,2nr -k3,3n" \
    -D mapreduce.job.reduces=3 \
    -files task3_sort_mapper.py,task3_sort_reducer.py \
    -mapper "python3 task3_sort_mapper.py" \
    -reducer "python3 task3_sort_reducer.py" \
    -input "$AGG_OUTPUT" \
    -output "$FINAL_OUTPUT" \
    -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner

if [ $? -ne 0 ]; then
    echo "Job 3 failed."
    exit 1
fi

echo "Job 3 completed."


# ------------------------------------------------------------
# Clean intermediate results
# ------------------------------------------------------------

hadoop fs -rm -r -f "$JOIN_OUTPUT"
hadoop fs -rm -r -f "$AGG_OUTPUT"


echo "Task 3 completed successfully."
echo "Final output: /Output/task3"
