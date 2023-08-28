#!/usr/bin/env python3

import json
import sys
import math
from collections import defaultdict


def read_test_symbols(path):
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return data


def read_test_estimation(path):
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return data


def calculate_total_test_time(test_symbols, test_estimation):
    total_test_time = 0
    test_time_per_target = {}
    for test_target_name, test_methods in test_symbols.items():
        target_test_time = 0
        for test_method in test_methods:
            # TODO: get an estimation of the missing test method
            testTime = test_estimation.get(test_method, 0.0)
            target_test_time += testTime
            test_time_per_target[test_target_name] = target_test_time

        total_test_time += target_test_time
    return total_test_time, test_time_per_target


def shard_one_test_target(test_methods, group_count, test_estimation):
    filtered_test_estimation = {k:v for k,v in test_estimation.items() if k in test_methods }
    sorted_test_estimation = sorted(filtered_test_estimation.items(), key=lambda item: item[1], reverse=True)
    # print(sorted_test_estimation)

    groups = [[] for _ in range(group_count)]
    for i, (task, _) in enumerate(sorted_test_estimation):
        groups[i % group_count].append((task))
    return groups


def shard_test(test_symbols, test_estimation, jobs, test_time_per_target, no_sharding_labels, optimal_test_time):
    test_plan = {}

    for test_label, test_methods in test_symbols.items():
        print(f"Sharding 'ios_unit_test' target: {test_label}")
        if test_label in no_sharding_labels:
            if test_label not in test_plan:
                test_plan[test_label] = {}
            test_plan[test_label]["0"] = test_methods
            continue

        total_test_time = test_time_per_target[test_label]
        count = math.ceil(1.0 * total_test_time / optimal_test_time)
        shard_lists = shard_one_test_target(test_methods, count, test_estimation)
        
        for index, methods in enumerate(shard_lists):
            if test_label not in test_plan:
                test_plan[test_label] = {}
            test_plan[test_label][index] = methods 

    return test_plan


def write_test_plan(output_path, data):
     with open(output_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

def main():
    jobs = sys.argv[1]

    test_symbols_file = sys.argv[2]
    test_symbols = read_test_symbols(test_symbols_file)

    test_estimation_file = sys.argv[3]
    test_estimation = read_test_estimation(test_estimation_file)

    output_file = sys.argv[4]

    no_sharding_labels = set(sys.argv[5:])
    
    total_test_time, test_time_per_target = calculate_total_test_time(test_symbols, test_estimation)
    optimal_test_time = total_test_time / int(jobs)

    test_plan = shard_test(test_symbols, test_estimation, jobs, test_time_per_target, no_sharding_labels, optimal_test_time)
    write_test_plan(output_file, test_plan)

    


if __name__ == "__main__":
    main()