import re

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
    successors = []

    # First pass: collect basic block information without successors
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
            enable_disable_calls = []

        for resource_name in shared_resource_names:
            if resource_name in line:
                shared_resources.append(line.strip())

        if 'enable_isr' in line or 'disable_isr' in line:
            enable_disable_calls.append(line.strip())

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
            if block.shared_resources or block.enable_disable_calls:
                block.code.append(line)

    return blocks

shared_resource_input = input("Enter the names of shared resources, separated by commas: ")
shared_resource_names = [name.strip() for name in shared_resource_input.split(',')]

file_path = r"C:\BA\Github\BADataRaces\Racebench\2.1\svp_simple_001\advanced1self.c.011t.cfg"
blocks = parse_basic_blocks(file_path, shared_resource_names)

for (func_name, bb_num), bb in blocks.items():
    if bb.shared_resources or bb.enable_disable_calls:
        print(bb)
