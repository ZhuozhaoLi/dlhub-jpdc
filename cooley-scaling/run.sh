#!/bin/bash


max_workers_per_node=12
trials=5
walltime="00:40:00"
tasks=1000
priming=2000
endpoint_name="dlhub-cooley"
queue='default'
#queue='debug-flat-quad'
for c in "noop" "oqmd" "matminer-featurize" "matminer-util" "cifar10" "inception";
#for c in "noop";
do
    for i in 1 2 4 8 12 24 48 96 192 384;
    #for i in 4;
    do
        echo "Running with $i $c containers"
        echo "priming with $(($i * 4)) tasks"
        python run.py -i $i -n $trials -c $c -a $max_workers_per_node -t $tasks -w $walltime -y $endpoint_name -p $(($i * 4))
    done
done
