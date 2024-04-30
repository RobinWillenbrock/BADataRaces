#include <iostream>
#include <thread>

int count = 0;

void threadFunction(int& count) {
    if (count == 0) 
        count++;
}

int main() {
    std::thread t1(threadFunction, std::ref(count));
    std::thread t2(threadFunction, std::ref(count)); 

    t1.join();
    t2.join();
    std::cout << count << std::endl;
    return 0;
}
