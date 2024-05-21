#include <iostream>

int shared_variable = 0;

void isr() {
    shared_variable++;
}

int main() {
    isr();

    for (int i = 0; i < 1000000; i++) {
<<<<<<< HEAD

=======
        
>>>>>>> ae153c0013b71fcf0f9e8d6cc8b4810b150d08bd
        shared_variable++;
    }

    std::cout << "Shared variable value: " << shared_variable << std::endl;

    return 0;
}
