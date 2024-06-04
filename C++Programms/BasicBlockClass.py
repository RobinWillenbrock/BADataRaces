import re

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
file_path = r"C:\BA\Github\BADataRaces\Racebench\case13iflock.c.011t.cfg"
blocks = parse_basic_blocks(file_path, shared_resource_names)

for (func_name, bb_num), bb in blocks.items():
    print(bb)
