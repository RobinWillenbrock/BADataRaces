import re
def extract_basic_blocks(cfg_file, block_ids, output_file):
    with open(cfg_file, 'r') as f:
        cfg_content = f.read()

    extracted_blocks = ""

    for block_id in block_ids:
        pattern = r'<bb ' + str(block_id) + r'> :(?:\s|.)*?(?=<bb \d+> :|\s*}\s*\n)'
        basic_block = re.search(pattern, cfg_content, re.DOTALL)

        if basic_block:
            extracted_blocks += basic_block.group(0) + '\n\n'
        else:
            print("Basic block with ID {} not found in the CFG file.".format(block_id))

    
    with open(output_file, 'w') as f:
        f.write(extracted_blocks)

<<<<<<< HEAD
cfg_file = "C++Programms\\Beispiel.cpp.011t.cfg"
=======
cfg_file = "C++Programms\\BeispielCFG-Beispiel.cpp.015t.cfg"
>>>>>>> 64765ac2fb91c92977ca361fd8bbdf9ea1976081
output_file = "extracted_blocks.txt"
block_ids = input("Enter the IDs of the basic blocks to extract (separated by spaces): ").split()
block_ids = [int(block_id) for block_id in block_ids]
extract_basic_blocks(cfg_file, block_ids, output_file)
