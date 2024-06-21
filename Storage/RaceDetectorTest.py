import re
from collections import defaultdict

class BasicBlock:
    def __init__(self, function_name, number, shared_resources=None, successors=None, enable_disable_calls=None, code=None):
        self.function_name = function_name
        self.number = number
        self.shared_resources = shared_resources if shared_resources else []
        self.successors = successors if successors else []
        self.enable_disable_calls = enable_disable_calls if enable_disable_calls else []
        self.code = code if code else []

    def __repr__(self):
        return (f"BasicBlock(function_name={self.function_name}, number={self.number}, shared_resources={self.shared_resources}, "
                f"successors={[succ.number for succ in self.successors]}, enable_disable_calls={self.enable_disable_calls}, "
                f"code={' '.join(self.code)})")

def parse_basic_blocks(file_path, shared_resource_names):
    blocks = {}
    current_function = None

    with open(file_path, 'r') as file:
        lines = file.readlines()

    bb_num = None
    shared_resources = []
    enable_disable_calls = []
    line_number = 0  # Track line numbers

    # First pass: collect basic block information without successors
    for line in lines:
        line = line.strip()
        line_number += 1

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
            enable_disable_calls = []
            successors = []

        for resource_name in shared_resource_names:
            if re.search(fr'\b{resource_name}\b', line):
                if re.search(fr'\b{resource_name}\b\s*=', line):
                    shared_resources.append((resource_name, 'write', line_number))
                else:
                    shared_resources.append((resource_name, 'read', line_number))

        if 'enable_isr' in line or 'disable_isr' in line:
            enable_disable_calls.append((line.strip(), line_number))

    # Add the last parsed block
    if bb_num is not None and current_function is not None:
        blocks[(current_function, bb_num)] = BasicBlock(current_function, bb_num, shared_resources, successors, enable_disable_calls)

    # Second pass: collect successors and code lines for relevant blocks
    current_function = None
    bb_num = None
    for line in lines:
        line = line.strip()

        func_match = re.match(r';; Function (.+?) \(', line)
        if func_match:
            current_function = func_match.group(1)
            bb_num = None
            continue

        if 'succs' in line:
            succ_match = re.match(r';; (\d+) succs \{(.+?)\}', line)
            if succ_match:
                bb_num = int(succ_match.group(1))
                succ_list = [int(succ.strip()) for succ in succ_match.group(2).split()]
                if (current_function, bb_num) in blocks:
                    blocks[(current_function, bb_num)].successors = [blocks[(current_function, succ)] for succ in succ_list if (current_function, succ) in blocks]
            continue  # Skip the line with successors information

        bb_match = re.match(r'<bb (\d+)>:', line)
        if bb_match:
            bb_num = int(bb_match.group(1))

        if bb_num is not None and (current_function, bb_num) in blocks:
            block = blocks[(current_function, bb_num)]
            block.code.append(line)

    return blocks

def track_isr_status(blocks):
    isr_count = len(set(block.function_name for block in blocks.values() if re.search(r'isr[_]?\d+', block.function_name)))
    return [0] * isr_count  # Initialize ISR status array with zeros

def detect_isr_enabling_relationships(blocks):
    isr_enabling = defaultdict(list)
    for block in blocks.values():
        for call, line_number in block.enable_disable_calls:
            if "enable_isr" in call:
                enabler_isr_match = re.search(r'isr[_]?(\d+)', block.function_name)
                enabled_isr_match = re.search(r'enable_isr\s*\((\d+)\)', call)
                if enabler_isr_match and enabled_isr_match:
                    enabler_isr = int(enabler_isr_match.group(1))
                    enabled_isr = int(enabled_isr_match.group(1))
                    isr_enabling[enabler_isr].append(enabled_isr)
                    print(f"ISR {enabler_isr} can enable ISR {enabled_isr} (line {line_number} in block {block.number})")
    return isr_enabling

def detect_data_races(blocks):
    potential_data_races = []
    resource_accesses = defaultdict(list)
    isr_status = track_isr_status(blocks)
    isr_enabling = detect_isr_enabling_relationships(blocks)

    def dfs(block, visited_blocks, access_list, current_isr_status, path):
        if (block.function_name, block.number) in visited_blocks:
            return
        visited_blocks.add((block.function_name, block.number))
        path.append((block.function_name, block.number))

        for call, line_number in block.enable_disable_calls:
            isr_idx_match = re.search(r'\((\d+)\)', call)
            if isr_idx_match:
                isr_idx = int(isr_idx_match.group(1)) - 1  # Convert to 0-based index
                if "disable_isr" in call:
                    if 0 <= isr_idx < len(current_isr_status):
                        current_isr_status[isr_idx] = 1
                        print(f"ISR {isr_idx+1} disabled at line {line_number} in block {block.number}")
                elif "enable_isr" in call:
                    if 0 <= isr_idx < len(current_isr_status):
                        current_isr_status[isr_idx] = 0
                        print(f"ISR {isr_idx+1} enabled at line {line_number} in block {block.number}")

        for resource, access_type, line_number in block.shared_resources:
            print(f"Accessing shared resource '{resource}' in block {block.number} at line {line_number} with ISR Status: {current_isr_status}")
            access_list.append((block.function_name, block.number, resource, access_type, line_number, current_isr_status.copy()))
            resource_accesses[resource].append((block.function_name, block.number, access_type, line_number, current_isr_status.copy()))

        if not block.successors:
            print(f"Path: {path}, ISR Status: {current_isr_status}")
        else:
            for successor in block.successors:
                dfs(successor, visited_blocks.copy(), access_list.copy(), current_isr_status.copy(), path.copy())

    # Start DFS from each entry block
    for (func_name, bb_num), block in blocks.items():
        if bb_num == 2:  # Assuming entry block is always <bb 2>
            dfs(block, set(), [], isr_status.copy(), [])

    def check_for_data_races():
        for resource, accesses in resource_accesses.items():
            for i, (func1, bb_num1, access_type1, line_number1, isr_status1) in enumerate(accesses):
                for j, (func2, bb_num2, access_type2, line_number2, isr_status2) in enumerate(accesses):
                    if i >= j:
                        continue  # Avoid duplicate checks and self-comparisons
                    if func1 != func2 and (access_type1 == "write" or access_type2 == "write"):
                        print(f"Checking potential data race: {func1} (BB {bb_num1}, Line {line_number1}) with ISR Status: {isr_status1} and {func2} (BB {bb_num2}, Line {line_number2}) with ISR Status: {isr_status2}")
                        potential_data_races.append((resource, (func1, bb_num1, access_type1, line_number1, isr_status1),
                                                     (func2, bb_num2, access_type2, line_number2, isr_status2)))

    check_for_data_races()

    # Filter out false positives where ISR is disabled during access
    def filter_data_races(potential_data_races):
        filtered_data_races = []
        for resource, access1, access2 in potential_data_races:
            func1, bb_num1, access_type1, line_number1, isr_status1 = access1
            func2, bb_num2, access_type2, line_number2, isr_status2 = access2

            def is_isr_disabled(isr_status, func_name):
                isr_match = re.search(r'isr[_]?(\d+)', func_name)
                if isr_match:
                    isr_number = int(isr_match.group(1))
                    if isr_number <= len(isr_status):
                        return isr_status[isr_number - 1] == 1
                return False

            relevant_isr_disabled1 = is_isr_disabled(isr_status1, func2)  # Check if the ISR in func2 is disabled in isr_status1
            relevant_isr_disabled2 = is_isr_disabled(isr_status2, func1)  # Check if the ISR in func1 is disabled in isr_status2
            
            # Check enabling relationships
            def are_related_isrs_disabled(isr_status, func_name, isr_enabling):
                isr_match = re.search(r'isr[_]?(\d+)', func_name)
                if isr_match:
                    isr_number = int(isr_match.group(1))
                    related_isrs = isr_enabling.get(isr_number, [])
                    if related_isrs:
                        return all(isr_status[related_isr - 1] == 1 for related_isr in related_isrs)
                return True

            related_isr_disabled1 = are_related_isrs_disabled(isr_status1, func2, isr_enabling)
            related_isr_disabled2 = are_related_isrs_disabled(isr_status2, func1, isr_enabling)

            print(f"Filtering: {func1} (BB {bb_num1}, Line {line_number1}) ISR Status: {isr_status1}, {func2} (BB {bb_num2}, Line {line_number2}) ISR Status: {isr_status2}, relevant_isr_disabled1: {relevant_isr_disabled1}, relevant_isr_disabled2: {relevant_isr_disabled2}, related_isr_disabled1: {related_isr_disabled1}, related_isr_disabled2: {related_isr_disabled2}")

            if not (relevant_isr_disabled1 or relevant_isr_disabled2 or (not related_isr_disabled1) or (not related_isr_disabled2)):
                filtered_data_races.append((resource, access1, access2))

        return filtered_data_races

    filtered_data_races = filter_data_races(potential_data_races)

    return filtered_data_races

# Main execution
shared_resource_input = input("Enter the names of shared resources, separated by commas: ")
shared_resource_names = [name.strip() for name in shared_resource_input.split(',')]

file_path = r"C:\BA\Github\BADataRaces\Racebench\2.1\svp_simple_001\advanced1self.c.011t.cfg"
blocks = parse_basic_blocks(file_path, shared_resource_names)

data_races = detect_data_races(blocks)

print("Detected Data Races:")
for resource, access1, access2 in data_races:
    print(f"Resource: {resource}")
    print(f"  Access 1: Function {access1[0]} (BB {access1[1]}), {access1[2]}, Line {access1[3]}, ISR Status: {access1[4]}")
    print(f"  Access 2: Function {access2[0]} (BB {access2[1]}), {access2[2]}, Line {access2[3]}, ISR Status: {access2[4]}")
    print()
