#kubectl delete deployments -n dlhub-privileged --all --grace-period=0 --cascade=true
#kubectl delete services -n dlhub-privileged --all
#kubectl delete replicasets -n dlhub-privileged --all


#kubectl delete pods -n dlhub-privileged --all
kubectl get pods -n dlhub-privileged --no-headers=true | awk '/dlhub-funcx/{print $1}' | xargs kubectl -n dlhub-privileged delete pod
