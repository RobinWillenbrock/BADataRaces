from threading import Thread, Lock

class BasicBlock:
    def __init__(self, name):
        self.name = name
        self.instructions = []

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

class CriticalVariable:
    def __init__(self, name):
        self.name = name
        self.lock = Lock()
        self.value = 0

    def increment(self):
        with self.lock:
            self.value += 1

    def decrement(self):
        with self.lock:
            self.value -= 1

    def get_value(self):
        with self.lock:
            return self.value

def simulate_block(block, critical_variables):
    for instruction in block.instructions:
        for var_name in critical_variables:
            if var_name in instruction:
                if "increment" in instruction:
                    critical_variables[var_name].increment()
                elif "decrement" in instruction:
                    critical_variables[var_name].decrement()

def main():
    # Accept critical variable names as input
    num_critical_vars = int(input("Enter the number of critical variables: "))
    critical_variables = {}
    for i in range(num_critical_vars):
        var_name = input(f"Enter the name of critical variable {i+1}: ")
        critical_variables[var_name] = CriticalVariable(var_name)

    # Simulate concurrent access to critical variables within each basic block
    # Here you'll need to implement the logic to parse the .cfg file and extract basic blocks

    # Example basic blocks (replace with parsing logic)
    basic_blocks = {"BB1": BasicBlock("BB1"), "BB2": BasicBlock("BB2")}

    for block_name, block in basic_blocks.items():
        thread = Thread(target=simulate_block, args=(block, critical_variables))
        thread.start()

    # Wait for the threads to finish
    for thread in threads:
        thread.join()

    # Check for potential data races
    for var_name, var in critical_variables.items():
        if var.get_value() != 0:
            print(f"Data race detected on {var_name}")

if __name__ == "__main__":
    main()
