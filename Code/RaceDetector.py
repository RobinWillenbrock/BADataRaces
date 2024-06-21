import re
from collections import defaultdict
# comments would be nice

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
    # do you remove bloxks without SR/disable/enable?
    blocks = {}
    current_function = None

    with open(file_path, 'r') as file:
        lines = file.readlines()

    bb_num = None
    shared_resources = []
    enable_disable_calls = []
    code_lines = []
    line_number = 0  

    for line in lines:
        line = line.strip()
        line_number += 1

        func_match = re.match(r';; Function (.+?) \(', line)
        if func_match:
            if bb_num is not None and current_function is not None:
                blocks[(current_function, bb_num)] = BasicBlock(current_function, bb_num, shared_resources, [], enable_disable_calls, code_lines)
            current_function = func_match.group(1)
            # Isn't a reset of SR, enable/disable, lines necessary here?
            bb_num = None
            continue

        bb_match = re.match(r'<bb (\d+)>:', line)
        if bb_match:
            if bb_num is not None and current_function is not None:
                blocks[(current_function, bb_num)] = BasicBlock(current_function, bb_num, shared_resources, [], enable_disable_calls, code_lines)
            bb_num = int(bb_match.group(1))
            shared_resources = []
            enable_disable_calls = []
            code_lines = []

        for resource_name in shared_resource_names:
            if re.search(fr'\b{resource_name}\b', line):
                # what about += ?
                if re.search(fr'\b{resource_name}\b\s*=', line):
                    # what about comparison (resource == ... )?
                    shared_resources.append((resource_name, 'write', line_number))
                else:
                    shared_resources.append((resource_name, 'read', line_number))

        if 'enable_isr' in line or 'disable_isr' in line:
            enable_disable_calls.append((line.strip(), line_number))
        # why also lines without SR/disable/enable?
        code_lines.append((line, line_number))

    if bb_num is not None and current_function is not None:
        blocks[(current_function, bb_num)] = BasicBlock(current_function, bb_num, shared_resources, [], enable_disable_calls, code_lines)

    current_function = None
    bb_num = None
    # not feasible within one iteration?
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
    return blocks

def track_isr_status(blocks):
    isr_count = len(set(block.function_name for block in blocks.values() if re.search(r'isr[_]?\d+', block.function_name)))
    return [0] * isr_count

def extract_isr_index(function_name):
    match = re.search(r'isr[_]?(\d+)', function_name)
    if match:
        return int(match.group(1)) - 1
    return None


resource_accesses = defaultdict(list)
isr_enabling_map = defaultdict(set)
potential_data_races = []

def process_block(block, current_isr_status):
    # iterate all lines in block to updated isr vector
    for line, line_number in block.code:
        if 'enable_isr' in line or 'disable_isr' in line:
            isr_idx_match = re.search(r'\((\d+)\)', line)
            if isr_idx_match:
                isr_idx = int(isr_idx_match.group(1)) - 1  
                if "disable_isr" in line:
                    if 0 <= isr_idx < len(current_isr_status):
                        current_isr_status[isr_idx] = 1
                elif "enable_isr" in line:
                    if 0 <= isr_idx < len(current_isr_status):
                        current_isr_status[isr_idx] = 0
        
        # update list of accesses with ISR vector
        for resource_name, access_type, res_line_number in block.shared_resources:
            if res_line_number == line_number:
                resource_accesses[resource_name].append((block.function_name, block.number, access_type, line_number, current_isr_status.copy()))

def dfs(block, visited_blocks, current_isr_status, path):
    if (block.function_name, block.number) in visited_blocks:
        return
    visited_blocks.add((block.function_name, block.number))
    path.append((block.function_name, block.number))

    # what about current isr status on merge of two paths?
    # -> if I get it right, your method only copys the status of the block that was visited first
    process_block(block, current_isr_status)
    if not block.successors:
        return
    else:
        for successor in block.successors:
            dfs(successor, set(visited_blocks), current_isr_status.copy(), path.copy())

def is_isr_disabled(isr_status, func_name):
    isr_idx = extract_isr_index(func_name)
    if isr_idx is not None and isr_idx < len(isr_status):
        # returns whether the isr is enabled, not whether it is disabled
        return isr_status[isr_idx] == 1
    return False

def is_isr_enabled_by_another(isr_status, func_name):
    isr_idx = extract_isr_index(func_name)
    # why no check for valid isr number here but at other places? (isr_idx<len(isr_status))
    if isr_idx is not None:
        for enabler_isr, enabled_isrs in isr_enabling_map.items():
            enabler_idx = extract_isr_index(enabler_isr)
            if enabler_idx is not None and not is_isr_disabled(isr_status, enabler_isr):
                if isr_idx in enabled_isrs:
                    return True
    return False

def check_for_data_races():
    for resource, accesses in resource_accesses.items():
        for i, (func1, bb_num1, access_type1, line_number1, isr_status1) in enumerate(accesses):
            for j, (func2, bb_num2, access_type2, line_number2, isr_status2) in enumerate(accesses):
                if i >= j:
                    continue  
                if func1 != func2 and (access_type1 == "write" or access_type2 == "write"):
                    potential_data_races.append((resource, (func1, bb_num1, access_type1, line_number1, isr_status1),
                                                    (func2, bb_num2, access_type2, line_number2, isr_status2)))

def filter_data_races(potential_data_races):
    filtered_data_races = []
    for resource, access1, access2 in potential_data_races:
        func1, _, _, _, isr_status1 = access1
        func2, _, _, _, isr_status2 = access2
        # not correct since disabled function not correct?
        relevant_isr_disabled1 = is_isr_disabled(isr_status1, func2) and not is_isr_enabled_by_another(isr_status1, func2)
        relevant_isr_disabled2 = is_isr_disabled(isr_status2, func1) and not is_isr_enabled_by_another(isr_status2, func1)

        if not (relevant_isr_disabled1 or relevant_isr_disabled2):
            filtered_data_races.append((resource, access1, access2))

    return filtered_data_races

def detect_data_races(blocks):
    for block in blocks.values():
        for call, _ in block.enable_disable_calls:
            # store in dict which interrupts are enabled by which interrupt
            # -> what if disable after enable?
            if 'enable_isr' in call:
                isr_idx_match = re.search(r'\((\d+)\)', call)
                if isr_idx_match:
                    enabled_isr_idx = int(isr_idx_match.group(1)) - 1
                    enabler_isr = block.function_name
                    isr_enabling_map[enabler_isr].add(enabled_isr_idx)
    for (func_name, bb_num), block in blocks.items():
        if bb_num == 2: 
            # process initial block and perform DFS 
            initial_isr_status = track_isr_status(blocks).copy()
            process_block(block, initial_isr_status)
            for successor in block.successors:
                dfs(successor, set(), initial_isr_status.copy(), [(func_name, bb_num)])
    check_for_data_races()
    filtered_data_races = filter_data_races(potential_data_races)
    return filtered_data_races

if __name__ == "__main__":
    shared_resource_input = input("Enter the names of shared resources, separated by commas: ")
    shared_resource_names = [name.strip() for name in shared_resource_input.split(',')]

    file_path = input("Enter the file path: ").strip()
    blocks = parse_basic_blocks(file_path, shared_resource_names)

    data_races = detect_data_races(blocks)

    print("Detected Data Races:")
    for resource, access1, access2 in data_races:
        print(f"Resource: {resource}")
        print(f"  Access 1: Function {access1[0]} (BB {access1[1]}), {access1[2]}, Line {access1[3]}, ISR Status: {access1[4]}")
        print(f"  Access 2: Function {access2[0]} (BB {access2[1]}), {access2[2]}, Line {access2[3]}, ISR Status: {access2[4]}")
        print()
