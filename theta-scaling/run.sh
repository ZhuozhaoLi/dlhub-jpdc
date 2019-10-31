#!/bin/bash


max_workers_per_node=64
trials=5
walltime="00:60:00"
tasks=1000
priming=2000
endpoint_name="dlhub-theta-remote"
queue='default'
#queue='debug-flat-quad'
#for c in "noop" "oqmd" "matminer-featurize" "matminer-util" "cifar10" "inception";
for c in "matminer-util";
do
    for i in 16 32 64 128 256 512;
    # for i in 2;
    do
        echo "Running with $i $c containers"
        echo "priming with $(($i * 4 + 50)) tasks"
        python run.py -i $i -n $trials -c $c -a $max_workers_per_node -t $tasks -w $walltime -y $endpoint_name -p $(($i * 4 + 50))
    done
done
