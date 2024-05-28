import os
import re
from itertools import combinations

# Define a class to represent an ISR
class ISR:
    def __init__(self, name):
        self.name = name
        self.shared_resources = set()

    def add_shared_resource(self, resource):
        self.shared_resources.add(resource)

    def has_shared_resource(self, resource):
        return resource in self.shared_resources

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
        lines = block.split('\n')
        for idx, line in enumerate(lines):
            for resource in shared_resources:
                if resource in line:
                    if re.search(rf'\b{resource}\b\s*=', line):
                        operations.append((resource, 'write', idx + 1))  # line number within the block
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

def detect_data_races(operations1, operations2, isr_states):
    races = []
    shared_resources = set(resource for resource, _, _ in operations1).intersection(
                        resource for resource, _, _ in operations2)

    for resource, op_type1, line1 in operations1:
        if resource in shared_resources:
            # Check if any ISR is currently disabled for the shared resource
            if any(isr_states.get(resource, [0])):
                for resource2, op_type2, line2 in operations2:
                    if resource == resource2:
                        if op_type1 == 'write' or op_type2 == 'write':
                            races.append((resource, op_type1, "File 1", line1, op_type2, "File 2", line2))
    return races





def link_isr_with_resources(file_contents):
    isrs = {}
    isr_pattern = re.compile(r'isr\d*')

    for filepath, content in file_contents.items():
        filename = os.path.basename(filepath)
        if 'isr' in filename:
            isr_match = isr_pattern.search(filename)
            if isr_match:
                isr_name = isr_match.group()
                if isr_name not in isrs:
                    isrs[isr_name] = ISR(isr_name)
                shared_resources = re.findall(r'\bg1_case13\b', content)  # Modify the regex to match "g1_case13"
                print(f"Found shared resources in {isr_name}: {shared_resources}")
                for resource in shared_resources:
                    isrs[isr_name].add_shared_resource(resource)
    
    return isrs



def main():
    folder = input("Enter the path to the folder containing the function files: ")
    shared_resources = input("Enter the shared resources, separated by commas: ").split(',')
    shared_resources = [res.strip() for res in shared_resources]

    file_contents = {}
    priorities = {}
    isrs = {}  # Initialize the ISRs dictionary

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            content = read_function_from_file(filepath)
            if content:
                file_contents[filepath] = content
                priorities[filepath] = get_priority(filepath)

    # Link ISRs with shared resources
    isrs = link_isr_with_resources(file_contents)

    # Initialize ISR states for all ISRs as enabled (0)
    isr_states = {isr_name: [0] for isr_name in isrs.keys()}

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

        races = detect_data_races(operations1, operations2, isr_states)

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


