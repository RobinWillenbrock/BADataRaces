#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

// Define a structure to represent a variable access
struct VariableAccess {
    std::string variable;
    std::string location;
};

// Function to parse the CFG file and extract variable accesses
void parseCFG(const std::string& cfgFilePath, std::unordered_map<std::string, std::vector<VariableAccess>>& variableAccesses) {
    std::ifstream cfgFile(cfgFilePath);
    std::string line;

    while (std::getline(cfgFile, line)) {
        // Example line: "  %0 = variable"
        if (line.find(" = variable") != std::string::npos) {
            std::istringstream iss(line);
            std::string token;
            std::string variableName;

            // Split the line by spaces
            while (iss >> token) {
                if (token == "=") {
                    // The variable name should be the previous token
                    break;
                }
                variableName = token;
            }

            // Extract the line number as location
            size_t pos = line.find(":");
            std::string location = line.substr(0, pos);

            // Store the variable access
            variableAccesses[variableName].push_back({variableName, location});
        }
    }
}

// Function to detect data races
void detectDataRaces(const std::unordered_map<std::string, std::vector<VariableAccess>>& variableAccesses) {
    // Loop through each variable
    for (const auto& pair1 : variableAccesses) {
        const std::string& variable = pair1.first;
        const std::vector<VariableAccess>& accesses = pair1.second;

        // Check for potential data races
        if (accesses.size() > 1) {
            std::cout << "Potential data race for variable " << variable << ":" << std::endl;
            for (const VariableAccess& access : accesses) {
                std::cout << "  Location: " << access.location << std::endl;
            }
        }
    }
}

int main() {
    // Provide the path to the CFG file
    std::string cfgFilePath = "C:\C++Programms\Calculator\Calculator.cpp.011t.cfg";

    // Map to store variable accesses
    std::unordered_map<std::string, std::vector<VariableAccess>> variableAccesses;

    // Parse the CFG file
    parseCFG(cfgFilePath, variableAccesses);

    // Detect data races
    detectDataRaces(variableAccesses);

    return 0;
}
