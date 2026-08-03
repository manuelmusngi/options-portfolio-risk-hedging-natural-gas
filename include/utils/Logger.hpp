#pragma once
#include <string>

namespace hedging {

class Logger {
public:
    enum class Level { Info, Warning, Error };

    static void log(Level level, const std::string& msg);
    static void info(const std::string& msg);
    static void warn(const std::string& msg);
    static void error(const std::string& msg);
};

}
