import os
import re
from itertools import combinations

class BasicBlock:
    def __init__(self, function_name, number, shared_resources=None, successors=None, enable_disable_calls=None):
        self.function_name = function_name
        self.number = number
        self.shared_resources = shared_resources if shared_resources else []
        self.successors = successors if successors else []
        self.enable_disable_calls = enable_disable_calls if enable_disable_calls else []

    def __repr__(self):
        return (f"BasicBlock(function_name={self.function_name}, number={self.number}, shared_resources={self.shared_resources}, "
                f"successors={self.successors}, enable_disable_calls={self.enable_disable_calls})")


def parse_basic_blocks(file_path, shared_resource_names):
    blocks = {}
    current_function = None

    with open(file_path, 'r') as file:
        lines = file.readlines()

    bb_num = None
    shared_resources = []
    successors = []
    enable_disable_calls = []

    for line in lines:
        line = line.strip()

        func_match = re.match(r';; Function (.+?) \(', line)
        if func_match:
            if bb_num is not None and current_function is not None:
                blocks[(current_function, bb_num)] = BasicBlock(current_function, bb_num, shared_resources, successors, enable_disable_calls)
            current_function = func_match.group(1)
            bb_num = None
            continue

        bb_match = re.match(r'<bb (\d+)>:', line)
        if bb_match:
            if bb_num is not None and current_function is not None:
                blocks[(current_function, bb_num)] = BasicBlock(current_function, bb_num, shared_resources, successors, enable_disable_calls)
            bb_num = int(bb_match.group(1))
            shared_resources = []
            successors = []
            enable_disable_calls = []

        if 'goto' in line:
            succ = int(line.split('<bb ')[1].split('>')[0])
            successors.append(succ)

        for resource_name in shared_resource_names:
            if resource_name in line:
                shared_resources.append(line.strip())

        if 'enable_isr' in line or 'disable_isr' in line:
            enable_disable_calls.append(line.strip())

    if bb_num is not None and current_function is not None:
        blocks[(current_function, bb_num)] = BasicBlock(current_function, bb_num, shared_resources, successors, enable_disable_calls)
    
    return blocks


shared_resource_input = input("Enter the names of shared resources, separated by commas: ")
shared_resource_names = [name.strip() for name in shared_resource_input.split(',')]

# Use raw string literal to avoid issues with backslashes
file_path = r"C:\BA\Github\BADataRaces\Racebench\2.1\svp_simple_013\svp_simple_013_changed.c.011t.cfg"
blocks = parse_basic_blocks(file_path, shared_resource_names)

for (func_name, bb_num), bb in blocks.items():
    print(bb)

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
    in_critical_section = False

    for block in basic_blocks:
        lines = block.split('\n')
        for idx, line in enumerate(lines):
            if re.search(r'\block\s*\(\s*\)', line):
                in_critical_section = True
            elif re.search(r'\bunlock\s*\(\s*\)', line):
                in_critical_section = False

            if not in_critical_section:
                for resource in shared_resources:
                    if resource in line:
                        if re.search(rf'\b{resource}\b\s*=', line):
                            operations.append((resource, 'write', idx + 1)) 
                        elif re.search(rf'\b{resource}\b', line):
                            operations.append((resource, 'read', idx + 1))
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
    if priority1 == priority2:
        return [] 
    
    races = []
    shared_resources = set(resource for resource, _, _ in operations1).intersection(
                        resource for resource, _, _ in operations2)

    for resource, op_type1, line1 in operations1:
        if resource in shared_resources:
            for resource2, op_type2, line2 in operations2:
                if resource == resource2:
                    if op_type1 == 'write' or op_type2 == 'write':
                        races.append((resource, op_type1, "File 1", line1, op_type2, "File 2", line2))
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
            for resource, op_type1, func1, line1, op_type2, func2, line2 in races:
                print(f"\nResource: {resource}")
                print(f"{func1} - Operation: {op_type1} at line {line1}")
                print(f"{func2} - Operation: {op_type2} at line {line2}")
        else:
            print(f"No data races detected between {file1} and {file2}.")

if __name__ == "__main__":
    main()
