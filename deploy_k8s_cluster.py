import subprocess
import os

def run_command(command, check=True):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
    return result.stdout.strip()

def command_exists(command):
    """Check if a command exists on the system."""
    return subprocess.run(f"command -v {command}", shell=True, capture_output=True).returncode == 0

def main():
    # Check if VirtualBox is installed
    if not command_exists("virtualbox"):
        print("VirtualBox is not installed. Please install VirtualBox and try again.")
        return
    else:
        print("VirtualBox is already installed.")
        run_command("sudo apt-get update")
        run_command(f"sudo apt-get install -y linux-headers-$(uname -r) build-essential dkms")
        run_command("sudo apt-get install -y virtualbox-dkms")
        run_command("sudo modprobe vboxdrv")
        run_command("sudo modprobe vboxnetflt")
        run_command("sudo modprobe vboxnetadp")

    # Check if Vagrant is installed
    if not command_exists("vagrant"):
        print("Vagrant is not installed. Please install Vagrant and try again.")
        return
    else:
        print("Vagrant is already installed.")

    # Create a Vagrantfile for the Kubernetes cluster
    vagrantfile_content = """
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
          mkdir -p $HOME/.kube
          sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
          sudo chown $(id -u):$(id -g) $HOME/.kube/config
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
    """

    with open("Vagrantfile", "w") as f:
        f.write(vagrantfile_content)

    # Start the Vagrant environment with VirtualBox as the provider
    run_command("vagrant up --provider=virtualbox")

    # Get the join command from the master
    join_command = run_command("vagrant ssh k8s-master -c 'kubeadm token create --print-join-command'")

    # Join the worker to the cluster
    run_command(f"vagrant ssh k8s-worker -c 'sudo {join_command}'")

    print("Kubernetes cluster deployment is complete.")

if __name__ == "__main__":
    main()
