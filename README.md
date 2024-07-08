# kubeadm-and-Vagrant
 It includes the installation of VirtualBox if it's not already installed. The script assumes you're running on a Debian-based system (like Ubuntu).

 
# This script does the following: #

1. Checks if VirtualBox and Vagrant are installed, and installs them if they are not.

2. Creates a Vagrantfile that defines a master node and a worker node, sets up Docker and Kubernetes on both, and initializes the Kubernetes master.

3. Starts the Vagrant environment.

4. Retrieves the join command from the master node and uses it to join the worker node to the cluster.


You can run this script with ' ./deploy_k8s_cluster.sh '
