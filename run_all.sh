mkdir -p results

binalyzer() {
  mkdir -p results/binalyzer
  docker build -f binalyzer.docker -t syscall_extraction:binalyzer .
  docker run --name syscall_analysis syscall_extraction:binalyzer
  docker cp syscall_analysis:/usr/src/app/results ./results/binalyzer
  docker rm syscall_analysis
  mv ./results/binalyzer/results/* ./results/binalyzer
  rmdir ./results/binalyzer/results
}

sysfilter() {
  mkdir -p results/sysfilter
  docker build -f sysfilter.docker -t syscall_extraction:sysfilter .
  docker run --name syscall_analysis syscall_extraction:sysfilter
  docker cp syscall_analysis:/usr/src/app/results ./results/sysfilter
  docker rm syscall_analysis
  mv ./results/sysfilter/results/* ./results/sysfilter
  rmdir ./results/sysfilter/results
}

confine() {
  mkdir -p results/confine
  if [ ! -d "./confine" ]; then
    git clone https://github.com/shamedgh/confine.git
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.7
    sudo apt install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo apt install -y sysdig
  fi
  python3 confine_runner.py
}

binalyzer
sysfilter
confine
