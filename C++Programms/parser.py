import re

def parse_cfg_data(cfg_file):
    basic_blocks = {}
    current_bb = None

    try:
        with open(cfg_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                print("Line:", line)  # Debug
                match = re.match(r'<bb (\d+)> :', line)
                if match:
                    bb_id = int(match.group(1))  # Extracting basic block ID
                    print("Basic block ID:", bb_id)  # Debug: Print the extracted ID
                    current_bb = {"id": bb_id, "successors": []}
                    basic_blocks[bb_id] = current_bb
                elif line.startswith("  if"):
                    # Extracting successor basic blocks from if statements
                    successors = line.split("{")[1].split("}")[0].strip().split()
                    current_bb["successors"] = [int(succ.strip("<>")) for succ in successors]
                elif line.startswith(" goto"):
                    # Extracting successor basic blocks from goto statements
                    successor_match = re.search(r'<bb (\d+)>', line)
                    if successor_match:
                        successor = int(successor_match.group(1))
                        current_bb["successors"].append(successor)
                    else:
                        print("Failed to extract successor ID from line:", line)
                elif line.startswith("goto"):
                    # Extracting successor basic blocks from goto statements without space
                    successor_match = re.search(r'<bb (\d+)>', line)
                    if successor_match:
                        successor = int(successor_match.group(1))
                        current_bb["successors"].append(successor)
                    else:
                        print("Failed to extract successor ID from line:", line)
    except FileNotFoundError as e:
        print("Failed to open file:", cfg_file)
        print("Error:", e)
    except Exception as e:
        print("An error occurred:", e)

    return basic_blocks

# File containing CFG data
cfg_file = "C++Programms/NewCFG-HelloWorld.cpp.015t.cfg"

# Parse CFG data
parsed_data = parse_cfg_data(cfg_file)

# Print basic blocks and their successors
if parsed_data:
    for bb_id, bb_data in parsed_data.items():
        print(f"Basic Block {bb_id}:")
        print("Successors:", bb_data["successors"])
        print()
else:
    print("No data parsed.")
