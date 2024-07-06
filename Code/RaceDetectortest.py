import re
from collections import defaultdict
import time

shared_resource_input = input("Enter the names of shared resources, separated by commas: ")
file_path = input("Enter the file path: ").strip()
start_time = time.time()

class BasicBlock:
    def __init__(self, function_name, number, priority, shared_resources=None, successors=None, enable_disable_calls=None, function_calls=None):
        self.function_name = function_name
        self.number = number
        self.priority = priority
        self.shared_resources = shared_resources if shared_resources else []
        self.successors = successors if successors else []
        self.enable_disable_calls = enable_disable_calls if enable_disable_calls else []
        self.function_calls = function_calls if function_calls else []

    def __repr__(self):
        return (f"BasicBlock(function_name={self.function_name}, number={self.number}, priority={self.priority}, shared_resources={self.shared_resources}, "
                f"successors={[succ.number for succ in self.successors]}, enable_disable_calls={self.enable_disable_calls}, function_calls={self.function_calls})")

def parse_basic_blocks(file_path, shared_resource_names):
    blocks = {}
    function_blocks = defaultdict(list)
    current_function = None

    with open(file_path, 'r') as file:
        lines = file.readlines()

    bb_num = None
    shared_resources = []
    enable_disable_calls = []
    function_calls = []
    line_number = 0

    for line in lines:
        line = line.strip()
        line_number += 1

        func_match = re.match(r';; Function (.+?) \(', line)
        if func_match:
            if bb_num is not None and current_function is not None:
                priority = determine_priority(current_function)
                blocks[(current_function, bb_num)] = BasicBlock(current_function, bb_num, priority, shared_resources, [], enable_disable_calls, function_calls)
                function_blocks[current_function].append(blocks[(current_function, bb_num)])
            current_function = func_match.group(1)
            bb_num = None
            continue

        bb_match = re.match(r'<bb (\d+)>:', line)
        if bb_match:
            if bb_num is not None and current_function is not None:
                priority = determine_priority(current_function)
                blocks[(current_function, bb_num)] = BasicBlock(current_function, bb_num, priority, shared_resources, [], enable_disable_calls, function_calls)
                function_blocks[current_function].append(blocks[(current_function, bb_num)])
            bb_num = int(bb_match.group(1))
            shared_resources = []
            enable_disable_calls = []
            function_calls = []

        for resource_name in shared_resource_names:
            if re.search(fr'\b{resource_name}\b', line):
                if re.search(fr'\b{resource_name}\b\s*=', line) and not re.search(fr'\b{resource_name}\b\s*==', line):
                    shared_resources.append((resource_name, 'write', line_number))
                else:
                    shared_resources.append((resource_name, 'read', line_number))

        if 'enable_isr' in line or 'disable_isr' in line:
            enable_disable_calls.append((line.strip(), line_number))

        call_match = re.match(r'.*call.*\b(\w+)\b', line)
        if call_match:
            function_calls.append((call_match.group(1), line_number))

    if bb_num is not None and current_function is not None:
        priority = determine_priority(current_function)
        blocks[(current_function, bb_num)] = BasicBlock(current_function, bb_num, priority, shared_resources, [], enable_disable_calls, function_calls)
        function_blocks[current_function].append(blocks[(current_function, bb_num)])

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

    return blocks, function_blocks

def determine_priority(function_name):
    match = re.search(r'isr[_]?(\d+)', function_name)
    if match:
        return int(match.group(1))  # Higher priority for lower ISR number
    return float('inf')  # Lower priority for non-ISR functions

def track_isr_status(blocks):
    isr_count = len(set(block.function_name for block in blocks.values() if re.search(r'isr[_]?\d+', block.function_name)))
    return [0] * isr_count  

def extract_isr_index(function_name):
    match = re.search(r'isr[_]?(\d+)', function_name)
    if match:
        return int(match.group(1)) - 1
    return None

def merge_isr_statuses(isr_status1, isr_status2):
    return [min(isr1, isr2) for isr1, isr2 in zip(isr_status1, isr_status2)]

def propagate_function_calls(blocks, function_blocks):
    for func_name, block_list in function_blocks.items():
        for block in block_list:
            for called_func, line_number in block.function_calls:
                if called_func in function_blocks:
                    for called_block in function_blocks[called_func]:
                        block.shared_resources.extend(called_block.shared_resources)
                        block.enable_disable_calls.extend(called_block.enable_disable_calls)

def detect_data_races(blocks):
    potential_data_races = []
    resource_accesses = defaultdict(list)
    isr_enabling_map = defaultdict(set)
    block_isr_statuses = defaultdict(list)

    for block in blocks.values():
        for call, line_number in block.enable_disable_calls:
            isr_idx_match = re.search(r'\((\d+)\)', call)
            if isr_idx_match:
                isr_idx = int(isr_idx_match.group(1)) - 1
                if 'enable_isr' in call:
                    enabler_isr = block.function_name
                    isr_enabling_map[enabler_isr].add(isr_idx)

    def process_block(block, current_isr_status):
        combined_events = sorted(
            block.shared_resources + block.enable_disable_calls,
            key=lambda x: x[2] if len(x) == 3 else x[1]
        )

        for event in combined_events:
            if isinstance(event, tuple) and len(event) == 3:  # This is a shared resource access
                resource_name, access_type, res_line_number = event
                resource_accesses[resource_name].append((block.function_name, block.number, access_type, res_line_number, current_isr_status.copy(), block.priority))
            elif isinstance(event, tuple) and len(event) == 2:  # This is an enable/disable ISR call
                call, line_number = event
                isr_idx_match = re.search(r'\((\d+)\)', call)
                if isr_idx_match:
                    isr_idx = int(isr_idx_match.group(1)) - 1  # Convert to 0-based index
                    if "disable_isr" in call:
                        if 0 <= isr_idx < len(current_isr_status):
                            current_isr_status[isr_idx] = 1
                    elif "enable_isr" in call:
                        if 0 <= isr_idx < len(current_isr_status):
                            current_isr_status[isr_idx] = 0

    def dfs(block, visited_blocks, current_isr_status, path):
        if (block.function_name, block.number) in visited_blocks:
            block_isr_statuses[(block.function_name, block.number)] = merge_isr_statuses(
                block_isr_statuses[(block.function_name, block.number)], current_isr_status)
            return
        visited_blocks.add((block.function_name, block.number))
        path.append((block.function_name, block.number))

        block_isr_statuses[(block.function_name, block.number)] = current_isr_status.copy()
        process_block(block, current_isr_status)

        if not block.successors:
            return
        else:
            for successor in block.successors:
                dfs(successor, set(visited_blocks), current_isr_status.copy(), path.copy())

    for (func_name, bb_num), block in blocks.items():
        if bb_num == 2:  
            initial_isr_status = track_isr_status(blocks).copy()
            process_block(block, initial_isr_status)
            for successor in block.successors:
                dfs(successor, set(), initial_isr_status.copy(), [(func_name, bb_num)])

    def check_for_data_races():
        for resource, accesses in resource_accesses.items():
            for i, (func1, bb_num1, access_type1, line_number1, isr_status1, priority1) in enumerate(accesses):
                for j, (func2, bb_num2, access_type2, line_number2, isr_status2, priority2) in enumerate(accesses):
                    if i >= j:
                        continue  
                    if func1 != func2 and (access_type1 == "write" or access_type2 == "write") and priority1 != priority2:
                        potential_data_races.append((resource, (func1, bb_num1, access_type1, line_number1, isr_status1, priority1),
                                                     (func2, bb_num2, access_type2, line_number2, isr_status2, priority2)))

    check_for_data_races()

    def filter_data_races(potential_data_races):
        filtered_data_races = []
        seen_races = set()

        for resource, access1, access2 in potential_data_races:
            func1, bb_num1, access_type1, line_number1, isr_status1, priority1 = access1
            func2, bb_num2, access_type2, line_number2, isr_status2, priority2 = access2

            def is_isr_disabled(isr_status, func_name):
                isr_idx = extract_isr_index(func_name)
                if isr_idx is not None and isr_idx < len(isr_status):
                    return isr_status[isr_idx] == 1
                return False

            def is_isr_enabled_by_another(isr_status, func_name):
                isr_idx = extract_isr_index(func_name)
                if isr_idx is not None:
                    for enabler_isr, enabled_isrs in isr_enabling_map.items():
                        enabler_idx = extract_isr_index(enabler_isr)
                        if enabler_idx is not None and not is_isr_disabled(isr_status, enabler_isr):
                            if isr_idx in enabled_isrs:
                                return True
                return False

            relevant_isr_disabled1 = is_isr_disabled(isr_status1, func2) and not is_isr_enabled_by_another(isr_status1, func2)
            relevant_isr_disabled2 = is_isr_disabled(isr_status2, func1) and not is_isr_enabled_by_another(isr_status2, func1)

            race_key = frozenset(((func1, line_number1), (func2, line_number2)))

            if not (relevant_isr_disabled1 or relevant_isr_disabled2) and race_key not in seen_races:
                filtered_data_races.append((resource, access1, access2))
                seen_races.add(race_key)

        return filtered_data_races

    filtered_data_races = filter_data_races(potential_data_races)

    return filtered_data_races


shared_resource_names = [name.strip() for name in shared_resource_input.split(',')]


blocks, function_blocks = parse_basic_blocks(file_path, shared_resource_names)


propagate_function_calls(blocks, function_blocks)

data_races = detect_data_races(blocks)

print("\nDetected Data Races:")
for resource, access1, access2 in data_races:
    print(f"Resource: {resource}")
    print(f"  Access 1: Function {access1[0]} (BB {access1[1]}), {access1[2]}, Line {access1[3]}, ISR Status: {access1[4]}, Priority: {access1[5]}")
    print(f"  Access 2: Function {access2[0]} (BB {access2[1]}), {access2[2]}, Line {access2[3]}, ISR Status: {access2[4]}, Priority: {access2[5]}")
    print()

end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")