#include <iostream>
#include <cstdlib>
#include <ctime>
#include <thread>

void threadFunction(const char* Variable1, const char* Variable2) {
    int count = 0;
    int random;

    while(count < 5){
        count++;
        random = rand() % 10;
        std::cout << random << std::endl;
        if (random % 2 == 0)
            std::cout << Variable1 << std::endl;
        else
            std::cout << Variable2 << std::endl;
    }
}

int main() {
    const char* Variable1 = "HelloWorld"; 
    const char* Variable2 = "HelloTUHH"; 

    srand(time(NULL));
    
    std::thread t1(threadFunction, Variable1, Variable2);
    std::thread t2(threadFunction, Variable1, Variable2);

    t1.join();
    t2.join();

    return 0;
}