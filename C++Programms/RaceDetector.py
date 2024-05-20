import re
import os

def read_function_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None

def extract_basic_blocks(func_content):
    # Regular expression to match basic blocks
    basic_block_pattern = re.compile(r'(<bb.*?>.*?)(?=<bb|\Z)', re.DOTALL)
    return basic_block_pattern.findall(func_content)

def find_operations(basic_blocks, shared_resources):
    operations = []
    for block in basic_blocks:
        for resource in shared_resources:
            if resource in block:
                if re.search(rf'\b{resource}\b\s*=', block):
                    operations.append((resource, 'write'))
                elif re.search(rf'\b{resource}\b', block):
                    operations.append((resource, 'read'))
    return operations

def get_priority(filename):
    # Extract the function type and number from the filename
    basename = os.path.basename(filename)
    if 'isr' in basename:
        match = re.search(r'isr(\d*)', basename)
        if match:
            return int(match.group(1)) if match.group(1) else 0
    return float('inf')  # main or non-isr functions get lowest priority

def detect_data_races(operations1, operations2, priority1, priority2):
    races = []
    for resource1, op_type1 in operations1:
        for resource2, op_type2 in operations2:
            if resource1 == resource2 and ((op_type1 == 'write') or (op_type2 == 'write')):
                if priority1 < priority2:
                    races.append((resource1, op_type1, "Function 1", op_type2, "Function 2"))
                else:
                    races.append((resource1, op_type2, "Function 2", op_type1, "Function 1"))
    return races

def main():
    file1 = input("Enter the path to the first function file: ")
    file2 = input("Enter the path to the second function file: ")
    shared_resources = input("Enter the shared resources, separated by commas: ").split(',')

    shared_resources = [res.strip() for res in shared_resources]

    func_content1 = read_function_from_file(file1)
    func_content2 = read_function_from_file(file2)

    if func_content1 is None or func_content2 is None:
        return

    priority1 = get_priority(file1)
    priority2 = get_priority(file2)

    basic_blocks1 = extract_basic_blocks(func_content1)
    basic_blocks2 = extract_basic_blocks(func_content2)

    operations1 = find_operations(basic_blocks1, shared_resources)
    operations2 = find_operations(basic_blocks2, shared_resources)

    races = detect_data_races(operations1, operations2, priority1, priority2)

    if races:
        print("Possible data races detected:")
        for resource, op_type1, func1, op_type2, func2 in races:
            print(f"\nResource: {resource}")
            print(f"{func1} - Operation: {op_type1}")
            print(f"{func2} - Operation: {op_type2}")
    else:
        print("No data races detected.")

if __name__ == "__main__":
    main()
