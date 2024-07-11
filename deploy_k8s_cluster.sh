#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Install VirtualBox if not installed
if ! command_exists virtualbox; then
    echo "VirtualBox is not installed. Installing VirtualBox..."
    sudo apt-get update
    sudo apt-get install -y virtualbox
else
    echo "VirtualBox is already installed."
fi

# Check if Vagrant is installed
if ! command_exists vagrant; then
    echo "Vagrant is not installed. Please install Vagrant."
    exit 1
else
    echo "Vagrant is already installed."
fi

# Create a Vagrantfile for the Kubernetes cluster
cat <<EOF > Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.define "k8s-master" do |master|
    master.vm.box = "ubuntu/bionic64"
    master.vm.hostname = "k8s-master"
    master.vm.network "private_network", type: "dhcp"
    master.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 2
    end
    master.vm.provision "shell", inline: <<-SHELL
      sudo apt-get update
      sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
      sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
      sudo apt-get update
      sudo apt-get install -y docker-ce
      sudo usermod -aG docker vagrant
      curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
      echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
      sudo apt-get update
      sudo apt-get install -y kubelet kubeadm kubectl
      sudo kubeadm init --pod-network-cidr=10.244.0.0/16
      mkdir -p \$HOME/.kube
      sudo cp -i /etc/kubernetes/admin.conf \$HOME/.kube/config
      sudo chown \$(id -u):\$(id -g) \$HOME/.kube/config
      kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
    SHELL
  end

  config.vm.define "k8s-worker" do |worker|
    worker.vm.box = "ubuntu/bionic64"
    worker.vm.hostname = "k8s-worker"
    worker.vm.network "private_network", type: "dhcp"
    worker.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 2
    end
    worker.vm.provision "shell", inline: <<-SHELL
      sudo apt-get update
      sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
      sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
      sudo apt-get update
      sudo apt-get install -y docker-ce
      sudo usermod -aG docker vagrant
      curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
      echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
      sudo apt-get update
      sudo apt-get install -y kubelet kubeadm kubectl
    SHELL
  end
end
EOF

# Start the Vagrant environment with VirtualBox as the provider
vagrant up --provider=virtualbox

# Get the join command from the master
JOIN_COMMAND=$(vagrant ssh k8s-master -c "kubeadm token create --print-join-command")

# Join the worker to the cluster
vagrant ssh k8s-worker -c "sudo $JOIN_COMMAND"

echo "Kubernetes cluster deployment is complete."

