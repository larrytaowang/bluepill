#!/usr/bin/env python3

import subprocess
import sys
import json
import zipfile
import tempfile
import os

# translation of this Bluepill code: https://github.com/MobileNativeFoundation/bluepill/blob/0ff8ffdadaa0f37bc906756e669627e8a66ff9f5/bp/src/BPXCTestFile.m#L18

def _extract_file_with_extension(zip_file_path, test_rule_name):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            if os.path.basename(file_info.filename) == test_rule_name:
                zip_ref.extract(file_info.filename, temp_dir)
                return os.path.join(temp_dir, file_info.filename)

    raise FileNotFoundError(f"Test bundle '{test_rule_name}' does not exist.")

def _nm_get_swift_symbol(bundle_path):
    testClassDict = {}

    nm_command = f"nm -gU {bundle_path} | cut -d' ' -f3 | xargs -s 131072 xcrun swift-demangle | cut -d' ' -f3 | grep -e '[\\.|_]'test"
    # output = subprocess.call(,shell=True)
    completed_process = subprocess.run(
            nm_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
    )
    output = completed_process.stdout.strip()

    testArray = output.split("\n")
    for testName in testArray:
        parts = testName.split(".")
        if len(parts) != 3:
            continue
        
        testClass = parts[1]
        if testClass not in testClassDict:
            testClassDict[testClass] = [] 

        testMethod = parts[2]
        if testMethod.startswith("test"):
            testClassDict[testClass].append(testMethod)

    return testClassDict
            

def _nm_get_objc_symbol(bundle_path):
    testClassDict = {}

    nm_command = f"nm -U {bundle_path} | grep ' t ' | cut -d' ' -f3,4 | cut -d'-' -f2 | cut -d'[' -f2 | cut -d']' -f1 | grep ' test'"
    completed_process = subprocess.run(
            nm_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
    )
    output = completed_process.stdout.strip()

    testArray = output.split("\n")
    for testName in testArray:
        parts = testName.split(" ")
        if len(parts) != 2:
            continue
        
        testClass = parts[0]
        if testClass not in testClassDict:
            testClassDict[testClass] = [] 

        testMethod = parts[1]
        testClassDict[testClass].append(testMethod)

    return testClassDict    


def _nm_get_symbol(bundle_path):
    if not os.path.exists(bundle_path):
        raise FileNotFoundError(f"The path '{bundle_path}' does not exist.")
    swift_symbols = _nm_get_swift_symbol(bundle_path)
    # objc_symbols = _nm_get_objc_symbol(bundle_path)

    merged_symbols = swift_symbols.copy()
    # merged_symbols.update(objc_symbols)

    return merged_symbols


#  @param test_target_dict: key: ios_unit_test rule name, value: test bundle path:
def generate_json(test_target_dict, output_path):
    symbol_data = {}
    for test_rule_name, test_bundle_zip_path in test_target_dict.items():
        xctest_path = _extract_file_with_extension(test_bundle_zip_path, test_rule_name)
        symbol_data[test_rule_name] = _nm_get_symbol(xctest_path)

    with open(output_path, "w") as json_file:
        json.dump(symbol_data, json_file, indent=4)

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <output_path> <json_encoded_dict>")
        return

    output_path = sys.argv[1]
    json_string = sys.argv[2]
    try:
        data = json.loads(json_string)
        generate_json(data, output_path)
    except json.JSONDecodeError:
        print("Invalid JSON argument.")

if __name__ == "__main__":
    main()



