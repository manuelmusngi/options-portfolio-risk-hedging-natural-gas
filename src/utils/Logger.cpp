#include "utils/Logger.hpp"
#include <iostream>
#include <mutex>

namespace hedging {

static std::mutex log_mutex;

void Logger::log(Level level, const std::string& msg) {
    std::lock_guard<std::mutex> lock(log_mutex);

    switch (level) {
        case Level::Info:    std::cout << "[INFO] "; break;
        case Level::Warning: std::cout << "[WARN] "; break;
        case Level::Error:   std::cout << "[ERROR] "; break;
    }
    std::cout << msg << "\n";
}

void Logger::info(const std::string& msg)  { log(Level::Info, msg); }
void Logger::warn(const std::string& msg)  { log(Level::Warning, msg); }
void Logger::error(const std::string& msg) { log(Level::Error, msg); }

}
