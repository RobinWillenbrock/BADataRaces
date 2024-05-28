import re
import os

def extract_functions_from_cfg(cfg_content, shared_variable):
    function_pattern = re.compile(r';; Function (.*?)\n(.*?)\n({.*?})\n\n', re.DOTALL)
    
    matches = function_pattern.findall(cfg_content)
    
    functions = {}
    for match in matches:
        func_name = match[0].split()[1].strip('()')
        func_signature = match[1].strip()
        func_body = filter_basic_blocks(match[2].strip(), shared_variable)
        if func_body:
            functions[func_name] = f"{func_signature}\n{func_body}"
    
    return functions

def filter_basic_blocks(func_body, shared_variable):
    basic_block_pattern = re.compile(r'(<bb.*?>.*?)(?=<bb|\Z)', re.DOTALL)
    
    filtered_body = []
    for block in basic_block_pattern.findall(func_body):
        if "unlock ()" in block or shared_variable in block or "lock ()" in block:
            filtered_body.append(block.strip())
    
    return '\n'.join(filtered_body) if filtered_body else None



def write_functions_to_files(functions):
    for func_name, func_content in functions.items():
        filename = f"{func_name}.c"
        with open(filename, 'w') as file:
            file.write(func_content)
        print(f"Written to {filename}")

def main():

    cfg_file_path = r"C:\BA\BADataRaces\Racebench\case13.c.011t.cfg"

    shared_variable = input("Enter the name of the shared variable: ")
    
    try:
        with open(cfg_file_path, 'r') as file:
            cfg_content = file.read()
        
        functions = extract_functions_from_cfg(cfg_content, shared_variable)
        if functions:
            write_functions_to_files(functions)
            print("All relevant functions have been written to separate files.")
        else:
            print(f"No basic blocks containing the variable '{shared_variable}' were found.")
        
    except FileNotFoundError:
        print(f"Error: The file at {cfg_file_path} was not found.")

if __name__ == "__main__":
    main()
