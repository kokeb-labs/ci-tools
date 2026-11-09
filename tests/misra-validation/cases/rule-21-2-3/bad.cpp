// Seeded violation: a shell command started from the program.
#include <cstdlib>

namespace kv::rule_21_2_3::bad {

int reset_device() { return std::system("reset-device --all"); }

}  // namespace kv::rule_21_2_3::bad
