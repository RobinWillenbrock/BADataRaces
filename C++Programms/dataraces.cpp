#include <iostream>
#include <fstream>
#include <string>
#include <unordered_set>

void parseAndAnalyzeCFG(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filename << std::endl;
        return;
    }

    std::unordered_set<std::string> accessedVariables;

    std::string line;
    while (std::getline(file, line)) {
        if (line.find("=") != std::string::npos) {
            size_t pos = line.find("="); 
            std::string variableName = line.substr(0, pos);
            variableName.erase(0, variableName.find_first_not_of(" \t\r\n"));
            variableName.erase(variableName.find_last_not_of(" \t\r\n") + 1);

            if (accessedVariables.find(variableName) != accessedVariables.end()) {
                std::cout << "Potential data race detected for variable: " << variableName << std::endl;
            } else {
                accessedVariables.insert(variableName);
            }
        }
    }

    file.close();
}
int main() {
    std::string cfgFile = "NewCFG-HelloWorld.cpp.015t.cfg";
    parseAndAnalyzeCFG(cfgFile);
    return 0;
}
