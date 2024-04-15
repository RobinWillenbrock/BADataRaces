#include <iostream>
#include <cstdlib>
#include <time.h>
int main() {
    const char* a = "HelloWorld"; 
    const char* b = "HelloTUHH"; 
    srand(time(NULL));
    int count = 0;
    int random;



while(count < 5){
    count = count +1;
    random = rand() % 10;
    std::cout << random << std::endl;
    if (random % 2 == 0)
        std::cout << a << std::endl;
    else
        std::cout << b << std::endl;
}
    if (random % 2 == 0){
        a = "ByeWorld"; 
        std::cout << a << std::endl;
    }else
    {
        a = "ByeTUHH";
        std::cout << a << std::endl;
    }
return 0;
}