import re

def find_successors(text):
    pattern = r';; (\d+) succs \{(.+?)\}'
    matches = re.findall(pattern, text)
    successors = {}

    for match in matches:
        number = int(match[0])
        numbers_in_brackets = map(int, match[1].split())
        if number not in successors:
            successors[number] = set(numbers_in_brackets)
        else:
            successors[number].update(numbers_in_brackets)

    return successors

file_path = "C++Programms\\NewCFGHelloWorld-HelloWorld.cpp.015t.cfg"

# Read the contents of the file
with open(file_path, 'r') as file:
    file_contents = file.read()

# Find and print successors
successors = find_successors(file_contents)
for number, successors_set in successors.items():
    if successors_set:
        print(f"Successors for {number}: {successors_set}")
    else:
        print(f"Successors for {number}: {{}}")

def find_variable_blocks(text, variables):
    pattern = r'<bb (\d+)> :([\s\S]*?)(?=(?:<bb \d+>)|\Z)'
    matches = re.findall(pattern, text)
    variable_blocks = {variable: set() for variable in variables}

    for match in matches:
        block_number = match[0]
        block_content = match[1]
        for variable in variables:
            if re.search(r'\b{}\b'.format(re.escape(variable)), block_content):
                variable_blocks[variable].add(block_number)

    return variable_blocks

file_path = "C++Programms\\NewCFGHelloWorld-HelloWorld.cpp.015t.cfg"

# Read the contents of the file
with open(file_path, 'r') as file:
    file_contents = file.read()

# Input variables to search for
input_variables = input("Enter the variables to search for (comma-separated): ").split(',')

# Find and print blocks containing the variables
variable_blocks = find_variable_blocks(file_contents, [variable.strip() for variable in input_variables])
for variable, blocks in variable_blocks.items():
    if blocks:
        print(f"The variable '{variable}' is found in the following blocks: {', '.join(blocks)}")
    else:
        print(f"The variable '{variable}' is not found in any blocks.")
