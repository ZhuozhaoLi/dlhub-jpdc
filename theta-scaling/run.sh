#!/bin/bash


max_workers_per_node=64
trials=10
walltime="00:15:00"
tasks=5000
endpoint_name="dlhub-theta-remote"
queue='default'
#queue='debug-flat-quad'
for i in 1 2 4 8 16 32 64 128 256 512;
do
    for c in "noop" "oqmd" "matminer-featurize" "matminer-util" "cifar10" "inception";
    do
        echo "Running with $i $c containers"
        python run.py -i $i -n $trials -c $c -a $max_workers_per_node -t $tasks -w $walltime -y $endpoint_name
    done
done
