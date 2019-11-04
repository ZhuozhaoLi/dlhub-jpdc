#!/bin/bash


trials=5
walltime="00:40:00"
tasks=1000
priming=2000
endpoint_name="dlhub-kube"
queue='default'
#queue='debug-flat-quad'
#for c in "noop" "oqmd" "matminer-featurize" "matminer-util" "cifar10" "inception";
for c in "oqmd" "matminer-util" "cifar10";
do
    #for i in 1 2 4 8 16 32 64 128 256 512;
    for i in 32 64 128 256 512;
    do
        echo "Running with $i $c containers"
        echo "priming with $(($i * 4)) tasks"
        python run.py -i $i -n $trials -c $c -t $tasks -w $walltime -y $endpoint_name -p $(($i * 10 + 50))
        ./del-all.sh
        sleep $(($i / 2 + 20))
    done
done
