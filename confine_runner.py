import json
from string import Template
import os
import sys

target_dir = 'targets'
results_dir = 'results'
work_dir = 'work_dir'
confine_dir = 'confine'
scripts_dir = 'confine_scripts'

if not os.path.exists(work_dir):
    os.makedirs(work_dir)
else:
    print(f'{work_dir} already exists, please remove it first')
    exit(1)

docker_template = Template(f"""
FROM ubuntu:22.04
COPY {work_dir}/$bin /$bin
COPY {work_dir}/run_$bin /script
ENTRYPOINT ["/script"]
""")

setting_template = Template("""
{
    "$bin-$config": {
        "enable": "true",
        "image-name": "syscall_extraction:confine_$bin-$config",
        "image-url": "syscall_extraction:confine_$bin-$config",
        "dependencies": {}
    }
}
""")


def create_container(bin, config):
    os.system(f'cp {target_dir}/{bin} {work_dir}/{bin}')
    os.system(f'cp {scripts_dir}/{config}/run_{bin}.sh {work_dir}/run_{bin}')
    os.system(f'chmod +x {work_dir}/run_{bin}')
    with open(f'{work_dir}/{bin}.docker', 'w') as f:
        f.write(docker_template.substitute(bin=bin))
    os.system(f'docker build -f {work_dir}/{bin}.docker -t syscall_extraction:confine_{bin}-{config} .')

def create_confine_settings(bin, config):
    with open(f'{work_dir}/{bin}-{config}.json', 'w') as f:
        f.write(setting_template.substitute(bin=bin, config=config))


def name_to_num(syscall_names):
    syscalls = {}
    nums = []
    with open('/usr/include/asm/unistd_64.h') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('#define __NR_'):
                line = line.replace('#define __NR_', '')
                syscall_name = line.split()[0]
                syscall_num = int(line.split()[1])
                syscalls[syscall_name] = syscall_num
                nums.append(syscall_num)
    blocked_syscall_nums = []
    for name in syscall_names:
        blocked_syscall_nums.append(syscalls[name])
    syscall_nums = []
    for num in nums:
        if num not in blocked_syscall_nums:
            syscall_nums.append(num)
    return syscall_nums


def get_results(bin, config):
    try:
        with open(f'{confine_dir}/results/syscall_extraction-confine_{bin}-{config}.seccomp.json') as f:
            res = json.load(f)
    except:
        print(f"Error in getting {bin}-{config}")
        return
    assert res["syscalls"][0]["action"] == "SCMP_ACT_ERRNO"
    syscalls = name_to_num(res["syscalls"][0]["names"])
    with open(f'{results_dir}/confine/{bin}-{config}_syscalls', 'w') as f:
        json.dump(syscalls, f)


def process_bin(bin, config):
    create_container(bin, config)
    create_confine_settings(bin, config)
    os.system(f'cp {work_dir}/{bin}-{config}.json {confine_dir}/settings_{bin}-{config}.json')
    os.chdir(f'{confine_dir}')
    os.system(
        f'sudo python3.7 confine.py -l libc-callgraphs/glibc.callgraph -m libc-callgraphs/musllibc.callgraph -i settings_{bin}-{config}.json -o output/ -p default.seccomp.json -r results/ -g go.syscalls/')
    os.chdir('..')
    get_results(bin, config)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 confine_runner.py <recover_results>")
        exit(1)
    recover = sys.argv[1].lower() == "true"

    for config in os.listdir(scripts_dir):
        for bin in os.listdir(f'{target_dir}'):
            if recover:
                get_results(bin, config)
                continue
            # Skip unstripped binaries to save time
            if "unstripped" in bin:
                continue
            # Skip already processed binaries
            if os.path.exists(f'{results_dir}/confine/{bin}-{config}_syscalls'):
                continue
            process_bin(bin, config)

    os.system(f"rm -rf {work_dir}")

if __name__ == '__main__':
    main()