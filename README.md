# kubeadm-and-Vagrant
 It includes the installation of VirtualBox if it's not already installed. The script assumes you're running on a Debian-based system (like Ubuntu).

 
# This script does the following: #

1. Checks if VirtualBox and Vagrant are installed, and installs them if they are not.

2. Creates a Vagrantfile that defines a master node and a worker node, sets up Docker and Kubernetes on both, and initializes the Kubernetes master.

3. Starts the Vagrant environment.

4. Retrieves the join command from the master node and uses it to join the worker node to the cluster.


You can run this script with ` ./deploy_k8s_cluster.sh `



# Instructions for Python

Save the script as ` deploy_k8s_cluster.py.`

Make the script executable (optional):

chmod +x deploy_k8s_cluster.py

## Run the script:

Copy code

` python3 deploy_k8s_cluster.py `

This Python script performs the same steps as the previous Bash script, ensuring that the necessary packages are installed, creating the Vagrantfile, and managing the Vagrant environment to deploy the Kubernetes cluster.
