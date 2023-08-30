#!/usr/bin/env python3

import json
import sys
import os
import subprocess

def read_json(path):
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return data

def write_bluepill_config_json_file(data, path):
    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def generate_bluepill_config_files(bluepill_config_template_path, ios_unit_test_label, sharding_plan, output_folder_path):
    generated_configs = []

    bluepill_config_template = read_json(bluepill_config_template_path)
    bluepill_config_template["no-split"] = [ios_unit_test_label]
        
    if len(sharding_plan) == 1:
        # If there is only one shard, no need to use 'exclude'/'include' attr
        bluepill_config = bluepill_config_template.copy()
        bluepill_config_path = os.path.join(output_folder_path, f"bluepill-{ios_unit_test_label}.json")
        write_bluepill_config_json_file(bluepill_config, bluepill_config_path)
        generated_configs.append(bluepill_config_path)
    else:
        # The last sharding should use exclude, all other sharding should use include
        dispatched_test_methods = []
        for index, test_methods in enumerate(sharding_plan):
            bluepill_config = bluepill_config_template.copy()
            bluepill_config_path = os.path.join(output_folder_path, f"bluepill-{ios_unit_test_label}-{index}.json")
            if index != len(sharding_plan) - 1:
                bluepill_config["include"] = test_methods
                dispatched_test_methods.extend(test_methods)
            else:
                bluepill_config["exclude"] = dispatched_test_methods

            write_bluepill_config_json_file(bluepill_config, bluepill_config_path)
            generated_configs.append(bluepill_config_path)
    
    return generated_configs


def generate_bazel_build_file(build_file_output_path, ios_unit_test_label, bluepill_configs):
    
    load_statement = """load("@bptestrunner//:bluepill_batch_test.bzl", "bluepill_batch_test")\n"""

    with open(build_file_output_path, "a") as f:
        f.write(load_statement)
        for index, config in enumerate(bluepill_configs):
            target_name = f"{ios_unit_test_label}-sharding-{index}"
            base_name = os.path.basename(config)

            bluepill_target = f"""
bluepill_batch_test(
    name = "{target_name}",
    test_targets = [
        "//:{ios_unit_test_label}",
    ],
    config_file = "bluepill_config/{base_name}",
)
"""
            f.write(bluepill_target)


def main():
    sharding_json_path = sys.argv[1]
    bluepill_config_template_path = sys.argv[2]
    # build_file_output_path = sys.argv[3]

    # output_folder_path = os.path.dirname(build_file_output_path)
    output_folder_path = sys.argv[3]

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    build_file_output_path = os.path.join(output_folder_path, "BUILD.bazel")
    with open(build_file_output_path, 'w') as f:
        pass  # This creates an empty file

    sharding_json = read_json(sharding_json_path)
   
    bluepill_output_folder = os.path.join(output_folder_path, "bluepill_config")
    if not os.path.exists(bluepill_output_folder):
        os.makedirs(bluepill_output_folder)
    for ios_unit_test_label, sharding_plan in sharding_json.items():
        bluepill_configs = generate_bluepill_config_files(bluepill_config_template_path, ios_unit_test_label, sharding_plan, bluepill_output_folder)
        generate_bazel_build_file(build_file_output_path, ios_unit_test_label, bluepill_configs)
            

if __name__ == "__main__":
    main()