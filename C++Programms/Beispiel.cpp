#include <iostream>

int shared_variable = 0;

void isr() {
    shared_variable++;
}

int main() {
    isr();

    for (int i = 0; i < 1000000; i++) {
        
        shared_variable++;
    }

    std::cout << "Shared variable value: " << shared_variable << std::endl;

    return 0;
}
