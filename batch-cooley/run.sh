#!/bin/bash


trials=5
walltime="01:00:00"
endpoint_name="dlhub-cooley-batching"
queue='debug'
tasks=1024
#queue='debug-flat-quad'
#for c in "noop" "oqmd" "matminer-featurize" "matminer-util" "cifar10" "inception";
for c in "cifar10" "inception";
do
    echo "Running with $c containers"
    python run.py -n $trials -c $c -w $walltime -y $endpoint_name -t $tasks
done
