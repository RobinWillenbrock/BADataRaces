#include <iostream>

int shared_variable = 0;

void isr() {
    shared_variable++;
}

int main() {
    // Simulate an interrupt triggering the ISR
    isr();

    // Simulate some work being done
    for (int i = 0; i < 1000000; i++) {
        // Some non-atomic operation
        shared_variable++;
    }

    std::cout << "Shared variable value: " << shared_variable << std::endl;

    return 0;
}
