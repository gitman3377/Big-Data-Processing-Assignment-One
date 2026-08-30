# Task 2 Clustering
#
# This script runs one MapReduce job per PAM iteration, with 3 reducers:
#   task2-mapper.py   gives every drop-off point to its closest medoid
#   task2-reducer.py  counts each cluster and picks its new medoid
#   task2-medoids.py  prints the report and says whether we can stop
#
# The loop ends when no medoid moves, or after v iterations, whichever comes
# first One last job then writes the final answer to /Output/task2

# Where everything lives on HDFS
# reading Trips.txt 
INPUT=/Input/Trips.txt
OUTPUT=/Output/task2
WORK=/Intermediate/task2                # working files, deleted at the end
REDUCERS=3

# initialization.txt has to be next to this script
if [ ! -f initialization.txt ]
then
    echo "ERROR: initialization.txt not found in the current directory."
    exit 1
fi

# Read initialization.txt The first line is v (how many iterations at most)
# and the lines after it are the k starting medoids The tr and sed remove
# Windows line endings and blank lines so the file always reads correctly
tr -d '\r' < initialization.txt | sed '/^[[:space:]]*$/d' > initialization.clean
V=`head -n 1 initialization.clean`
tail -n +2 initialization.clean > medoids.txt
K=`wc -l < medoids.txt`
rm -f initialization.clean

echo "PAM configuration: k = $K medoids, v = $V iterations, $REDUCERS reducers"

# Hadoop will not write into a folder that already exists, so clear old runs
hadoop fs -rm -r -f $OUTPUT
hadoop fs -rm -r -f $WORK

# The PAM loop Each turn is one full MapReduce job
converged=0
i=1
while [ $i -le $V ]
do
    # Give this iteration its own empty output folder
    hadoop fs -rm -r -f $WORK/iteration$i

    # medoids.txt is sent along with the code, so the mapper and reducer can
    # both open it by name on whichever machine they run on
    # python3 is named directly so the job does not depend on the python files
    # keeping their executable permission through a zip or a file transfer
    # KeyFieldBasedPartitioner on field 1 (the cluster number) sends cluster 0
    # to part-00000, cluster 1 to part-00001 and cluster 2 to part-00002, so
    # the merged output comes out in cluster order
    hadoop jar /usr/lib/hadoop/hadoop-streaming.jar \
    -D mapreduce.job.reduces=$REDUCERS \
    -D mapreduce.partition.keypartitioner.options=-k1,1 \
    -files task2-mapper.py,task2-reducer.py,medoids.txt \
    -mapper "python3 task2-mapper.py" \
    -reducer "python3 task2-reducer.py iterate" \
    -input $INPUT \
    -output $WORK/iteration$i \
    -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner

    # Stop straight away if the job did not work
    if [ $? -ne 0 ]
    then
        echo "ERROR: the MapReduce job of iteration $i failed."
        exit 1
    fi

    # Bring the few result lines (one per cluster) down to this machine
    rm -f iteration_output.txt
    hadoop fs -getmerge $WORK/iteration$i/part* iteration_output.txt

    # Print the report and work out the medoids for the next iteration
    python3 task2-medoids.py $i

    # The helper wrote 1 (stop) or 0 (keep going) into converged.txt
    seeiftrue=`cat converged.txt`
    mv medoids.next medoids.txt

    if [ $seeiftrue = 1 ]
    then
        converged=1
        echo ""
        echo "Converged after $i iteration(s): no medoid changed."
        break
    fi

    i=$((i+1))
done

# If we never converged we must have run out of iterations
if [ $converged -eq 0 ]
then
    echo ""
    echo "Stopped after the maximum of $V iteration(s)."
fi

# Last job It only assigns the points to the final medoids and writes the
# answer that gets marked: medoid_x, medoid_y, #points, avg_dissimilarity
# Same partitioner, so the three result lines stay in cluster order
hadoop jar /usr/lib/hadoop/hadoop-streaming.jar \
-D mapreduce.job.reduces=$REDUCERS \
-D mapreduce.partition.keypartitioner.options=-k1,1 \
-files task2-mapper.py,task2-reducer.py,medoids.txt \
-mapper "python3 task2-mapper.py" \
-reducer "python3 task2-reducer.py final" \
-input $INPUT \
-output $OUTPUT \
-partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner

if [ $? -ne 0 ]
then
    echo "ERROR: the final MapReduce job failed."
    exit 1
fi

# Tidy up the working files so only the final answer is left
hadoop fs -rm -r -f $WORK
rm -f iteration_output.txt converged.txt

# Show the result
echo ""
echo "Task 2 finished. Output written to $OUTPUT"
printf "medoid_x\tmedoid_y\t#points\tavg_dissimilarity\n"
hadoop fs -cat $OUTPUT/part*
