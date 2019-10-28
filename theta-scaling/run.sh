#!/bin/bash


max_workers_per_node=64
trials=1
walltime="00:60:00"
tasks=1000
priming=2000
endpoint_name="dlhub-theta-remote"
queue='default'
#queue='debug-flat-quad'
#for c in "noop" "oqmd" "matminer-featurize" "matminer-util" "cifar10" "inception";
for c in "inception";
do
    # for i in 2 4 8 16 32 64 128 256 512;
    for i in 512;
    do
        echo "Running with $i $c containers"
        python run.py -i $i -n $trials -c $c -a $max_workers_per_node -t $tasks -w $walltime -y $endpoint_name -p $priming
    done
done
