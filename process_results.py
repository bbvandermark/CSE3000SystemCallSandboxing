import json
import os

results_dir = 'results'
target_dir = 'targets'

def parse_binalyzer(bin):
    try:
        with open(f'{results_dir}/binalyzer/{bin}_syscalls') as f:
            lines = f.readlines()
            syscalls = []
            for line in lines:
                calls = line.split(' ')
                for call in calls:
                    syscalls.append(int(call))
        return syscalls
    except:
        return []


def parse_sysfilter(bin):
    try:
        with open(f'{results_dir}/sysfilter/{bin}_syscalls') as f:
            return json.load(f)
    except:
        return []


def parse_confine_config(bin, config):
    try:
        with open(f'{results_dir}/confine/{bin}-{config}_syscalls') as f:
            return json.load(f)
    except:
        return []


def parse_confine(bin, configs):
    results = {}
    for config in configs:
        results[config] = parse_confine_config(bin, config)
    return results


def num_to_name(syscall_nums):
    syscalls = ["" for _ in range(1000)]
    if os.path.exists('/usr/include/asm/unistd_64.h'):
        path = '/usr/include/asm/unistd_64.h'
    elif os.path.exists('/usr/include/x86_64-linux-gnu/asm/unistd_64.h'):
        path = '/usr/include/x86_64-linux-gnu/asm/unistd_64.h'
    else:
        print("could not open syscall defintion file")
        exit(1)
    with open(path) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('#define __NR_'):
                line = line.replace('#define __NR_', '')
                syscall_name = line.split()[0]
                syscall_num = int(line.split()[1])
                syscalls[syscall_num] = syscall_name
    syscall_names = []
    for num in syscall_nums:
        syscall_names.append(syscalls[num])
    return syscall_names


def process_syscall_list(syscalls):
    properties = {}
    properties['total'] = len(syscalls)
    properties['names'] = num_to_name(syscalls)
    return properties


def process_results(bin, configs):
    results = {}

    binalyzer = parse_binalyzer(bin)
    sysfilter = parse_sysfilter(bin)
    confine = parse_confine(bin, configs)

    if len(binalyzer) != 0 and len(sysfilter) == 0:
        static_analysis_intersection = binalyzer
    elif len(binalyzer) == 0 and len(sysfilter) != 0:
        static_analysis_intersection = sysfilter
    else:
        static_analysis_intersection = list(set(binalyzer) & set(sysfilter))

    confine_config_sets = []
    for config in confine:
        confine_config_sets.append(set(confine[config]))
    confine_config_union = list(set.intersection(*confine_config_sets))

    if len(confine_config_union) == 0:
        all_intersection = static_analysis_intersection
    else:
        all_intersection = list(set(static_analysis_intersection) & set(confine_config_union))

    results['binalyzer'] = process_syscall_list(binalyzer)
    results['sysfilter'] = process_syscall_list(sysfilter)
    results['static_analysis_intersection'] = process_syscall_list(static_analysis_intersection)

    confine_map = {}
    for config in confine:
        confine_map[config] = process_syscall_list(confine[config])
    results['confine'] = confine_map
    results['confine_config_union'] = process_syscall_list(confine_config_union)
    results['all_intersection'] = process_syscall_list(all_intersection)
    results['trimmed_by_confine_intersection'] = (
        list(set(results['static_analysis_intersection']['names']) - set(results['confine_config_union']['names'])))
    return results


def generate_latex_table(results, stripped):
    underscore_ecaped = lambda x: x.replace('_', '\_')
    header_names = [
        "$\\mathcal{B}$", # binalyzer
        "$\\mathcal{S}$", # sysfilter
        "$\\mathcal{C}_\\mathcal{M}$", # confine (minimal)
        "$\\mathcal{C}_\\mathcal{R}$", # confine (regular)
        "$\\mathcal{C}$", # confine (union)
        "$\\mathcal{B} \\cap \\mathcal{S}$",
        "$\\mathcal{B} \\cap \\mathcal{S} \\cap \\mathcal{C}$"
    ]
    table = "\\begin{table}[]\n"
    table += "\t\\begin{tabular}{|l|c|c|c|c|c|c|c|}\n"
    table += "\t\t\\hline\n"
    table += "\t\t\\textbf{Binary} & "
    table += ' & '.join(header_names)
    table += " \\\\ \\hline\n"
    for bin in sorted(results):
        if          "unstripped" in bin and stripped\
                or  "unstripped" not in bin and not stripped:
            continue
        table += f"\t\t{underscore_ecaped(bin)} & "
        table += f"{results[bin]['binalyzer']['total']} & "
        table += f"{results[bin]['sysfilter']['total']} & "
        table += f"{results[bin]['confine']['minimal']['total']} & "
        table += f"{results[bin]['confine']['regular_use']['total']} & "
        table += f"{results[bin]['confine_config_union']['total']} & "
        table += f"{results[bin]['static_analysis_intersection']['total']} & "
        table += f"{results[bin]['all_intersection']['total']} \\\\ \\hline\n"
    table += "\t\\end{tabular}\n"
    table += "\\end{table}\n"
    return table

def generate_interesting_trimmed_by_confine_table(results):
    underscore_ecaped = lambda x: x.replace('_', '\_')
    map = {}
    for bin in results['results']:
        if len(syscalls[bin]['trimmed_by_confine_intersection']) < 10:
            map[bin] = syscalls[bin]['trimmed_by_confine_intersection']
    table = "\\begin{table}[]\n"
    table += "\t\\begin{tabular}{|l|c|}\n"
    table += "\t\t\\hline\n"
    table += "\t\t\\textbf{Binary} & \\textbf{Trimmed by Confine} \\\\ \\hline\n"
    for bin in map:
        table += f"\t\t{underscore_ecaped(bin)} & "
        table += f"{map[bin]} \\\\ \\hline\n"
    table += "\t\\end{tabular}\n"
    table += "\\end{table}\n"
    return table


syscalls = {}
binalyzer_DNF = []
sysfilter_DNF = []
confine_DNF = {}

configs = []
for config in os.listdir('confine_scripts'):
    configs.append(config)

for bin in os.listdir(target_dir):
    results = process_results(bin, configs)
    if results['binalyzer']['total'] == 0:
        binalyzer_DNF.append(bin)
    if results['sysfilter']['total'] == 0:
        sysfilter_DNF.append(bin)
    for config in configs:
        if results['confine'][config]['total'] == 0:
            if config not in confine_DNF:
                confine_DNF[config] = []
            confine_DNF[config].append(bin)
    syscalls[bin] = results

results = {
    "results": syscalls,
    "binalyzer_DNF": binalyzer_DNF,
    "sysfilter_DNF": sysfilter_DNF,
    "confine_DNF": confine_DNF
}

with open('results.json', 'w') as f:
    f.write(json.dumps(results, indent=4, sort_keys=True))

