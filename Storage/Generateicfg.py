import re

def parse_cfg_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        function_name = ""
        nodes = set()
        edges = []
        function_calls = {}
        cfg_data = {}
        current_function = None
        in_cfg_section = False

        for line in lines:
            # Identify the function name
            if line.startswith(";; Function"):
                match = re.search(r'(\w+)\(', line)
                if match:
                    function_name = match.group(1)
                    current_function = function_name
                    nodes = set()
                    edges = []
                    function_calls[current_function] = []
                    cfg_data[function_name] = {'nodes': nodes, 'edges': edges}
            # Identify successors from comments
            succs_match = re.match(r';; (\d+) succs { (.*) }', line)
            if succs_match:
                src = succs_match.group(1)
                succs = succs_match.group(2).split()
                for succ in succs:
                    edges.append((src, succ.strip('{}')))
            # Identify basic blocks and edges
            bb_match = re.match(r'  <bb (\d+)>:', line)
            if bb_match:
                bb = bb_match.group(1)
                nodes.add(bb)
                in_cfg_section = True
            # Identify function calls within basic blocks
            if in_cfg_section:
                call_match = re.match(r'  (\w+)\s*\(.*\);', line)
                if call_match and current_function:
                    call = call_match.group(1)
                    function_calls[current_function].append((call, bb))
                    if call == "disable_isr" or call == "enable_isr":
                        edges.append((bb, call))
            # End of function block
            if line.strip() == "}":
                in_cfg_section = False

        return cfg_data, function_calls

def find_exit_node(nodes, edges):
    for node in nodes:
        is_exit = True
        for edge in edges:
            if edge[0] == node:
                is_exit = False
                break
        if is_exit:
            return node
    return None

def write_dot_file(cfg_data, function_calls, output_file):
    with open(output_file, 'w') as file:
        file.write("digraph ICFG {\n")
        # Write nodes and edges for each function CFG
        for function, data in cfg_data.items():
            for node in data['nodes']:
                file.write(f'  "{function}_{node}" [label="{function}:{node}"];\n')
            for edge in data['edges']:
                file.write(f'  "{function}_{edge[0]}" -> "{function}_{edge[1]}";\n')
        # Add edges for function calls
        for caller, calls in function_calls.items():
            for call, bb in calls:
                if call in cfg_data:
                    callee_entry_node = "2"  # Assuming <bb 2> as entry node of callee
                    file.write(f'  "{caller}_{bb}" -> "{call}_{callee_entry_node}";\n')
        file.write("}\n")

# Path to your .cfg file
cfg_file = "C:/BA/Github/BADataRaces/Code/Example1.cfg"
cfg_data, function_calls = parse_cfg_file(cfg_file)

# Print the parsed CFG data
for function, data in cfg_data.items():
    print(f"Function: {function}")
    print("Nodes:", data['nodes'])
    print("Edges:", data['edges'])

# Print the extracted function calls
print("Function Calls:")
for caller, calls in function_calls.items():
    print(f"{caller}: {calls}")

write_dot_file(cfg_data, function_calls, "icfg.dot")

print("ICFG written to icfg.dot")
