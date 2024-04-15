#include <iostream>

int main() {
    const char* a = "HelloWorld"; 
    const char* b = "HelloTUHH";  

    std::cout << a << std::endl;
    std::cout << b << std::endl;

    a = "ByeWorld"; 
    std::cout << a << std::endl;

    return 0;
}