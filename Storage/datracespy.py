import os

def parse_and_analyze_cfg(filename):
    try:
        with open(filename, 'r') as file:
            accessed_variables = set()

            for line in file:
                if "=" in line:
                    variable_name = line.split("=")[0].strip()

                    if variable_name in accessed_variables:
                        print("Potential data race detected for variable:", variable_name)
                    else:
                        accessed_variables.add(variable_name)

    except FileNotFoundError:
        print("Failed to open file:", filename)
    except PermissionError:
        print("Permission denied. Check file permissions.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    new_directory = "C:\BA\Github\BADataRaces\C++Programms"
    os.chdir(new_directory)
    cfg_file = "NewCFG-HelloWorld.cpp.015t.cfg"
    # Print the current working directory
    print("Current working directory:", os.getcwd())
    parse_and_analyze_cfg(cfg_file)
