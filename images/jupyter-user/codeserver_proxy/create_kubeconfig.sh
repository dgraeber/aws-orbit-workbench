#!/bin/bash

env_param='AWS_ORBIT_ENV='
ep=$(env | grep $env_param)
cluster_name=orbit-${ep/$env_param/}

user_param='AWS_ORBIT_TEAM_SPACE='
up=$(env | grep $user_param)
team_name=${up/$user_param/}

#server=$(aws eks describe-cluster --name $cluster_name --query 'cluster.endpoint' | sed "s/\"//g")
server=""
name=$(kubectl get secret -oname | grep $team_name-token)

ca=$(kubectl get $name -o jsonpath='{.data.ca\.crt}')
token=$(kubectl get $name -o jsonpath='{.data.token}' | base64 --decode)
namespace=$(kubectl get $name -o jsonpath='{.data.namespace}' | base64 --decode)

#echo $server
#echo $name
#echo $ca
#echo $token
#echo $namespace
#echo $team_name
#echo $cluster_name

if ! [ -d "/home/jovyan/.kube" ]; then
  mkdir /home/jovyan/.kube
fi

echo "
apiVersion: v1
kind: Config
clusters:
- name: ${cluster_name}-cluster
  cluster:
    certificate-authority-data: ${ca}
    server: ${server}
contexts:
- name: ${cluster_name}-context
  context:
    cluster: ${cluster_name}-cluster
    namespace: ${team_name}
    user: ${team_name}
current-context:  ${cluster_name}-context
users:
- name: ${team_name}
  user:
    token: ${token}
" > /home/jovyan/.kube/config

#mkdir /home/jovyan/.kube -p
#cp sa.kubeconfig /home/jovyan/.kube/config