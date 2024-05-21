import os
import re
from itertools import combinations

def read_function_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None

def extract_basic_blocks(func_content):
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
    basename = os.path.basename(filename)
    priority_offset = 0
    if 'isr' in basename:
        match = re.search(r'isr(\d*)_(high|low)', basename)
        if match:
            base_priority = int(match.group(1)) if match.group(1) else 0
            priority_level = match.group(2)
            if priority_level == 'high':
                priority_offset = -0.5
            elif priority_level == 'low':
                priority_offset = 0.5
            return base_priority + priority_offset
        else:
            match = re.search(r'isr(\d*)', basename)
            if match:
                base_priority = int(match.group(1)) if match.group(1) else 0
                return base_priority
    return float('inf')  

def detect_data_races(operations1, operations2, priority1, priority2):
    races = []
    locked_resources = set()  

    for resource, op_type in operations1:
        if op_type == 'write':
            for _, op_type2 in operations2:
                if op_type2 == 'write':
                    if resource in locked_resources:
                        break  
                    else:
                        races.append((resource, op_type, "File 1", op_type2, "File 2"))
                        break
            else:
                races.append((resource, op_type, "File 1", "read/write", "File 2"))
        elif op_type == 'read':
            for _, op_type2 in operations2:
                if op_type2 == 'write':
                    if resource in locked_resources:
                        break 
                    else:
                        races.append((resource, op_type, "File 1", op_type2, "File 2"))
                        break
    return races


def main():
    folder = input("Enter the path to the folder containing the function files: ")
    shared_resources = input("Enter the shared resources, separated by commas: ").split(',')
    shared_resources = [res.strip() for res in shared_resources]

    file_contents = {}
    priorities = {}

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            content = read_function_from_file(filepath)
            if content:
                file_contents[filepath] = content
                priorities[filepath] = get_priority(filepath)

    files = list(file_contents.keys())
    for file1, file2 in combinations(files, 2):
        func_content1 = file_contents.get(file1)
        func_content2 = file_contents.get(file2)
        
        if func_content1 is None or func_content2 is None:
            continue

        priority1 = priorities[file1]
        priority2 = priorities[file2]

        basic_blocks1 = extract_basic_blocks(func_content1)
        basic_blocks2 = extract_basic_blocks(func_content2)

        operations1 = find_operations(basic_blocks1, shared_resources)
        operations2 = find_operations(basic_blocks2, shared_resources)

        races = detect_data_races(operations1, operations2, priority1, priority2)

        if races:
            print(f"Possible data races detected between {file1} and {file2}:")
            for resource, op_type1, func1, op_type2, func2 in races:
                print(f"\nResource: {resource}")
                print(f"{func1} - Operation: {op_type1}")
                print(f"{func2} - Operation: {op_type2}")
        else:
            print(f"No data races detected between {file1} and {file2}.")

if __name__ == "__main__":
    main()